import requests

from .config import BASE_URL


class MyLib:

    def __init__(self):
        self.base_url = BASE_URL

    def send_greet(self, name: str):

        response = requests.post(
            f"{self.base_url}/greet",
            json={
                "name": name
            }
        )

        response.raise_for_status()

        return response.json()
