import requests

from app.config.settings import settings


class LinkedInClient:

    BASE_URL = "https://api.linkedin.com"

    def __init__(self):

        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN") or settings.LINKEDIN_ACCESS_TOKEN

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

    def _request(self, method, endpoint, **kwargs):

        response = requests.request(
            method=method,
            url=f"{self.BASE_URL}{endpoint}",
            headers=self._headers(),
            timeout=30,
            **kwargs
        )

        response.raise_for_status()

        return response

    def get(self, endpoint, params=None):

        return self._request(
            "GET",
            endpoint,
            params=params
        ).json()

    def post(self, endpoint, payload):

        return self._request(
            "POST",
            endpoint,
            json=payload
        )