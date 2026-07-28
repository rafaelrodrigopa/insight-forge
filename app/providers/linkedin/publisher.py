from .client import LinkedInClient


class LinkedInPublisher:

    def __init__(self):
        self.client = LinkedInClient()


    def publish_text(self, text, person_id):

        payload = {
            "author": f"urn:li:person:{person_id}",
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "lifecycleState": "PUBLISHED"
        }

        response = self.client.post(
            "/rest/posts",
            payload
        )

        return response.headers