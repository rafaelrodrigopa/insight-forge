import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID_LINKEDIN")
CLIENT_SECRET = os.getenv("CLIENT_SECRET_LINKEDIN")
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

print("Token carregado:")
print(ACCESS_TOKEN[:30] + "...")


response = requests.post(
    "https://www.linkedin.com/oauth/v2/introspectToken",
    data={
        "token": ACCESS_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
)

print("\nStatus:")
print(response.status_code)

print("\nResposta:")
print(response.json())