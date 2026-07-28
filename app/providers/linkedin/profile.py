from .client import LinkedInClient


class LinkedInProfile:

    def __init__(self):
        self.client = LinkedInClient()

    def get_profile(self):
        """
        Retorna informações do usuário autenticado no LinkedIn.
        """

        return self.client.get(
            "/v2/userinfo"
        )