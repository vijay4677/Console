import importlib.abc
import importlib.machinery
from urllib.parse import urlparse
import socket
import sys
from inspect import stack
from pathlib import Path

_FINDER_INSTALLED = False
_REQUESTS_PATCHED = False
_HTTPX_PATCHED = False
_URLLIB_PATCHED = False
_SOCKET_PATCHED = False
_ORIGINAL_REQUESTS_REQUEST = None
_ORIGINAL_HTTPX_CLIENT_REQUEST = None
_ORIGINAL_HTTPX_ASYNC_CLIENT_REQUEST = None
_ORIGINAL_URLLIB_OPEN = None
_ORIGINAL_SOCKET_CREATE_CONNECTION = None
_ORIGINAL_SOCKET_CONNECT = None
_ORIGINAL_SOCKET_CONNECT_EX = None


class DirectNetworkBlockedError(PermissionError):
    pass


_BLOCKED_HOSTS = {"localhost", "127.0.0.1"}
_BLOCKED_PORT = 8000


def is_called_from_mylib(package_name: str = "mylib1") -> bool:
    """
    Return True when the current call stack contains frames from mylib1.

    This is a debug helper, not a security boundary.
    """
    for frame_info in stack():
        filename = Path(frame_info.filename).as_posix()
        if package_name in filename:
            return True
    return False


def _block_if_direct(client_name: str):
    raise DirectNetworkBlockedError(
        f"Direct {client_name} network access is blocked. Use mylib1 instead of calling it directly."
    )


def _should_block_current_call(url_or_address) -> bool:
    if is_called_from_mylib():
        return False

    if isinstance(url_or_address, str):
        return _should_block_url(url_or_address)

    return _should_block_address(url_or_address)


def _should_block_host_port(host: str | None, port: int | None) -> bool:
    if host is None or port is None:
        return False

    return host.lower() in _BLOCKED_HOSTS and port == _BLOCKED_PORT


def _should_block_url(url: str) -> bool:
    parsed = urlparse(url)
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    return _should_block_host_port(parsed.hostname, port)


def _should_block_address(address) -> bool:
    if isinstance(address, tuple):
        host = address[0] if len(address) > 0 else None
        port = address[1] if len(address) > 1 else None
        return _should_block_host_port(host, port)

    return False


def _patch_requests_module(module):
    global _REQUESTS_PATCHED, _ORIGINAL_REQUESTS_REQUEST

    if _REQUESTS_PATCHED:
        return

    _ORIGINAL_REQUESTS_REQUEST = module.sessions.Session.request

    def guarded_request(self, method, url, **kwargs):
        if _should_block_current_call(url):
            _block_if_direct("requests")
        return _ORIGINAL_REQUESTS_REQUEST(self, method, url, **kwargs)

    module.sessions.Session.request = guarded_request
    _REQUESTS_PATCHED = True


def _patch_httpx_module(module):
    global _HTTPX_PATCHED, _ORIGINAL_HTTPX_CLIENT_REQUEST, _ORIGINAL_HTTPX_ASYNC_CLIENT_REQUEST

    if _HTTPX_PATCHED:
        return

    _ORIGINAL_HTTPX_CLIENT_REQUEST = module.Client.request
    _ORIGINAL_HTTPX_ASYNC_CLIENT_REQUEST = module.AsyncClient.request

    def guarded_client_request(self, method, url, **kwargs):
        if _should_block_current_call(str(url)):
            _block_if_direct("httpx")
        return _ORIGINAL_HTTPX_CLIENT_REQUEST(self, method, url, **kwargs)

    async def guarded_async_client_request(self, method, url, **kwargs):
        if _should_block_current_call(str(url)):
            _block_if_direct("httpx")
        return await _ORIGINAL_HTTPX_ASYNC_CLIENT_REQUEST(self, method, url, **kwargs)

    module.Client.request = guarded_client_request
    module.AsyncClient.request = guarded_async_client_request
    _HTTPX_PATCHED = True


def _patch_urllib_module(module):
    global _URLLIB_PATCHED, _ORIGINAL_URLLIB_OPEN

    if _URLLIB_PATCHED:
        return

    _ORIGINAL_URLLIB_OPEN = module.urlopen

    def guarded_urlopen(*args, **kwargs):
        target = None
        if args:
            target = args[0]
        elif "url" in kwargs:
            target = kwargs["url"]

        if isinstance(target, str) and _should_block_current_call(target):
            _block_if_direct("urllib")
        return _ORIGINAL_URLLIB_OPEN(*args, **kwargs)

    module.urlopen = guarded_urlopen
    _URLLIB_PATCHED = True


def _patch_socket_module():
    global _SOCKET_PATCHED, _ORIGINAL_SOCKET_CREATE_CONNECTION, _ORIGINAL_SOCKET_CONNECT, _ORIGINAL_SOCKET_CONNECT_EX

    if _SOCKET_PATCHED:
        return

    _ORIGINAL_SOCKET_CREATE_CONNECTION = socket.create_connection
    _ORIGINAL_SOCKET_CONNECT = socket.socket.connect
    _ORIGINAL_SOCKET_CONNECT_EX = socket.socket.connect_ex

    def guarded_create_connection(*args, **kwargs):
        address = args[0] if args else kwargs.get("address")
        if _should_block_current_call(address):
            _block_if_direct("socket")
        return _ORIGINAL_SOCKET_CREATE_CONNECTION(*args, **kwargs)

    def guarded_connect(self, address):
        if _should_block_current_call(address):
            _block_if_direct("socket")
        return _ORIGINAL_SOCKET_CONNECT(self, address)

    def guarded_connect_ex(self, address):
        if _should_block_current_call(address):
            _block_if_direct("socket")
        return _ORIGINAL_SOCKET_CONNECT_EX(self, address)

    socket.create_connection = guarded_create_connection
    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex
    _SOCKET_PATCHED = True


def _patch_loaded_modules():
    if "requests" in sys.modules:
        _patch_requests_module(sys.modules["requests"])

    if "httpx" in sys.modules:
        _patch_httpx_module(sys.modules["httpx"])

    if "urllib.request" in sys.modules:
        _patch_urllib_module(sys.modules["urllib.request"])

    _patch_socket_module()


class _GuardLoader(importlib.abc.Loader):
    def __init__(self, wrapped_loader, patch_fn):
        self._wrapped_loader = wrapped_loader
        self._patch_fn = patch_fn

    def create_module(self, spec):
        create_module = getattr(self._wrapped_loader, "create_module", None)
        if create_module is None:
            return None
        return create_module(spec)

    def exec_module(self, module):
        self._wrapped_loader.exec_module(module)
        self._patch_fn(module)


class _GuardFinder(importlib.abc.MetaPathFinder):
    def __init__(self, module_name, patch_fn):
        self._module_name = module_name
        self._patch_fn = patch_fn

    def find_spec(self, fullname, path, target=None):
        if fullname != self._module_name:
            return None

        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return spec

        spec.loader = _GuardLoader(spec.loader, self._patch_fn)
        return spec


def install_network_guard():
    global _FINDER_INSTALLED

    _patch_loaded_modules()

    if _FINDER_INSTALLED:
        return

    sys.meta_path.insert(0, _GuardFinder("requests", _patch_requests_module))
    sys.meta_path.insert(0, _GuardFinder("httpx", _patch_httpx_module))
    sys.meta_path.insert(0, _GuardFinder("urllib.request", _patch_urllib_module))
    _FINDER_INSTALLED = True
