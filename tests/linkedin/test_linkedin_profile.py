import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")


headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}


response = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers=headers
)


print("Status:", response.status_code)
print(response.json())