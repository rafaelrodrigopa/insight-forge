import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
PERSON_URN = os.getenv("LINKEDIN_PERSON_URN")


url = "https://api.linkedin.com/rest/posts"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "LinkedIn-Version": "202502",
    "X-Restli-Protocol-Version": "2.0.0"
}


payload = {
    "author": PERSON_URN,
    "commentary": "🚀 Primeiro teste de publicação usando o Insight Forge + LinkedIn API.",
    "visibility": "PUBLIC",
    "distribution": {
        "feedDistribution": "MAIN_FEED"
    },
    "lifecycleState": "PUBLISHED"
}


response = requests.post(
    url,
    headers=headers,
    json=payload
)


print(response.status_code)
print(response.text)