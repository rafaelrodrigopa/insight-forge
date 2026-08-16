from .client import LinkedInClient


class LinkedInAuth:

    def __init__(self):
        self.client = LinkedInClient()


    def get_profile(self):
        return self.client.get(
            "/v2/userinfo"
        )