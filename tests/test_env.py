from dotenv import load_dotenv
import os

load_dotenv()

print("LinkedIn ID:", os.getenv("CLIENT_ID_LINKEDIN"))
print("LinkedIn Secret:", os.getenv("CLIENT_SECRET_LINKEDIN"))
print("Gemini:", os.getenv("GEMINI_API_KEY"))