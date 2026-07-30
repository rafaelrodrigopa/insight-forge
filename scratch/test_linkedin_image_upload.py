import os
import requests
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.providers.linkedin import LinkedInPublisher

publisher = LinkedInPublisher()
author_urn = publisher._get_person_urn()

print("Author URN:", author_urn)

# Step 1: Initialize Upload
init_payload = {
    "initializeUploadRequest": {
        "owner": author_urn
    }
}

try:
    res = publisher.client.post("/rest/images?action=initializeUpload", init_payload)
    data = res.json()
    print("INITIALIZE UPLOAD OK:", data)
    
    upload_url = data["value"]["uploadUrl"]
    image_urn = data["value"]["image"]
    print("IMAGE URN:", image_urn)

    # Step 2: Upload binary bytes of an image if exists
    test_image = "posts/images/managing-imports-with-pythons-all.png"
    if os.path.exists(test_image):
        with open(test_image, "rb") as f:
            image_data = f.read()
        
        headers = {
            "Authorization": f"Bearer {publisher.client.access_token}",
            "Content-Type": "image/png"
        }
        put_res = requests.put(upload_url, headers=headers, data=image_data)
        print("PUT IMAGE STATUS:", put_res.status_code)

        # Step 3: Create Post with media attachment
        post_payload = {
            "author": author_urn,
            "commentary": "🚀 Teste de post com IMAGEM ANEXADA via API do LinkedIn!",
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

        post_res = publisher.client.post("/rest/posts", post_payload)
        print("POST WITH MEDIA STATUS:", post_res.status_code)
        print("POST ID:", post_res.headers.get("X-RestLi-Id"))

except Exception as e:
    print("ERRO:", e)
    if hasattr(e, "response") and e.response is not None:
        print("RESPONSE TEXT:", e.response.text)
