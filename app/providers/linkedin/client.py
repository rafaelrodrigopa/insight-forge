import os
import requests
from dotenv import load_dotenv


load_dotenv()


class LinkedInClient:

    BASE_URL = "https://api.linkedin.com"

    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

        if not self.access_token:
            raise ValueError(
                "LINKEDIN_ACCESS_TOKEN não encontrado no ambiente"
            )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202502",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    def get(self, endpoint, params=None):
        response = requests.get(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            params=params
        )

        response.raise_for_status()
        return response.json()

    def post(self, endpoint, payload):
        response = requests.post(
            f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            json=payload
        )

        response.raise_for_status()
        return response