from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    LINKEDIN_CLIENT_ID = os.getenv("CLIENT_ID_LINKEDIN")
    LINKEDIN_CLIENT_SECRET = os.getenv("CLIENT_SECRET_LINKEDIN")
    LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


settings = Settings()