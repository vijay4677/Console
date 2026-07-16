from .interceptor import install_network_guard

print("network_guard loaded")

install_network_guard()


def initialize():
    install_network_guard()
