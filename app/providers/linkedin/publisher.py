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

    def upload_image(self, image_path: str) -> str:
        """
        Realiza o upload de 2 etapas da imagem binária para a API de mídia do LinkedIn.
        Retorna o URN da imagem (ex: urn:li:image:...).
        """
        import os
        import requests

        author_urn = self._get_person_urn()
        init_payload = {
            "initializeUploadRequest": {
                "owner": author_urn
            }
        }

        res = self.client.post("/rest/images?action=initializeUpload", init_payload)
        data = res.json()
        upload_url = data["value"]["uploadUrl"]
        image_urn = data["value"]["image"]

        with open(image_path, "rb") as f:
            image_data = f.read()

        headers = {
            "Authorization": f"Bearer {self.client.access_token}",
            "Content-Type": "image/png"
        }
        put_res = requests.put(upload_url, headers=headers, data=image_data)
        put_res.raise_for_status()

        return image_urn

    def publish_image(self, text: str, image_path: str):
        """
        Publica um post no LinkedIn contendo uma imagem anexada e o texto formatado.
        """
        image_urn = self.upload_image(image_path)
        payload = {
            "author": self._get_person_urn(),
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "content": {
                "media": {
                    "id": image_urn
                }
            },
            "lifecycleState": "PUBLISHED"
        }

        return self.client.post("/rest/posts", payload)