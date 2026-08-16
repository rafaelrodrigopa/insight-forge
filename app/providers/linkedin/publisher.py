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

    def react_to_post(self, post_urn: str, reaction_type: str = "LIKE"):
        """
        Reage (curte/aplaude/etc) a um post do LinkedIn pelo URN do post.
        reaction_type: 'LIKE', 'PRAISE', 'EMPATHY', 'INTEREST', 'ENTERTAINMENT', 'APPRECIATION'
        """
        import urllib.parse
        encoded_urn = urllib.parse.quote(post_urn)
        payload = {
            "root": post_urn,
            "reactionType": reaction_type.upper()
        }
        return self.client.post("/rest/reactions", payload)

    def comment_on_post(self, post_urn: str, text: str):
        """
        Adiciona um comentário em um post do LinkedIn pelo URN do post.
        """
        import urllib.parse
        encoded_urn = urllib.parse.quote(post_urn)
        payload = {
            "actor": self._get_person_urn(),
            "message": {
                "text": text
            }
        }
        endpoint = f"/rest/socialActions/{encoded_urn}/comments"
        return self.client.post(endpoint, payload)

    def reshare_post(self, post_urn: str, commentary: str = ""):
        """
        Re-compartilha (reposta) um post do LinkedIn no seu próprio feed com um comentário opcional.
        """
        payload = {
            "author": self._get_person_urn(),
            "commentary": commentary,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "reshareContext": {
                "parent": post_urn
            },
            "lifecycleState": "PUBLISHED"
        }
        return self.client.post("/rest/posts", payload)