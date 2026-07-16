from .client import MyLib

_client = MyLib()


def send_greet(name: str):
    return _client.send_greet(name)