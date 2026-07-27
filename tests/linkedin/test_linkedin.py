import os
from dotenv import load_dotenv
import requests

load_dotenv()


code = os.getenv("LINKEDIN_AUTH_CODE")

response = requests.post(
    "https://www.linkedin.com/oauth/v2/accessToken",
    data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("CLIENT_ID_LINKEDIN"),
        "client_secret": os.getenv("CLIENT_SECRET_LINKEDIN"),
        "redirect_uri": "http://localhost:8000/callback"
    }
)

print(response.status_code)
print(response.json())