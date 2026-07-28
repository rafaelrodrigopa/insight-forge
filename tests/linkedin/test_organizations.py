import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

url = "https://api.linkedin.com/rest/organizationAcls"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "LinkedIn-Version": "202502",
    "X-Restli-Protocol-Version": "2.0.0"
}

params = {
    "q": "roleAssignee",
    "role": "ADMINISTRATOR"
}

response = requests.get(
    url,
    headers=headers,
    params=params
)

print(response.status_code)
print(response.text)