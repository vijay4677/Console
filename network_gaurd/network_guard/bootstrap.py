from .interceptor import install_network_guard

install_network_guard()


def initialize():
    install_network_guard()
