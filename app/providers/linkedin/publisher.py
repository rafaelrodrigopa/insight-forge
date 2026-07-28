from .client import LinkedInClient
from .profile import LinkedInProfile


class LinkedInPublisher:

    def __init__(self):
        self.client = LinkedInClient()
        self.profile = LinkedInProfile()


    def _get_person_urn(self):

        return self.profile.get_person_urn()


    def publish_text(self, text):
        """
        Publica um texto no LinkedIn.
        """

        payload = {
            "author": self._get_person_urn(),
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
        description=None
    ):
        """
        Publica um artigo/link no LinkedIn.
        """

        payload = {
            "author": self._get_person_urn(),
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


        if title or description:

            payload["content"]["article"]["title"] = title

            payload["content"]["article"]["description"] = description


        return self.client.post(
            "/rest/posts",
            payload
        )