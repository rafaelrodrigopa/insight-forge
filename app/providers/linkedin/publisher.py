from .client import LinkedInClient
from .profile import LinkedInProfile

class LinkedInPublisher:

    def __init__(self):
        self.client = LinkedInClient()
        self.profile = LinkedInProfile()


    def _get_person_urn(self):
        person_id = self.profile.get_person_id()

        return f"urn:li:person:{person_id}"


    def publish_text(self, text):
        """
        Publica um texto no LinkedIn.
        """

        person_urn = self._get_person_urn()

        payload = {
            "author": person_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "lifecycleState": "PUBLISHED"
        }

        return self.client.post(
            "/rest/posts",
            payload
        )


    def publish_article(
        self,
        text,
        url,
        title=None,
        description=None,
        person_urn=None
    ):
        """
        Publica um artigo/link no LinkedIn.
        """

        media = {
            "status": "READY",
            "originalUrl": url
        }


        if title:
            media["title"] = {
                "text": title
            }


        if description:
            media["description"] = {
                "text": description
            }


        payload = {
            "author": person_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "content": {
                "article": {
                    "source": url
                }
            },
            "lifecycleState": "PUBLISHED"
        }


        response = self.client.post(
            "/rest/posts",
            payload
        )

        return response