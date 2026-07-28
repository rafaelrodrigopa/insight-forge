from .client import LinkedInClient


class LinkedInProfile:

    def __init__(self):
        self.client = LinkedInClient()


    def get_profile(self):
        return self.client.get(
            "/v2/userinfo"
        )


    def get_person_id(self):
        profile = self.get_profile()

        return profile.get("sub")

    def get_person_urn(self):
        return f"urn:li:person:{self.get_person_id()}"