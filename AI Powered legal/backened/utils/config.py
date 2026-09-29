import os

from dotenv import load_dotenv


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-1.5-pro",
)

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
)

ALLOW_DEMO_MODE = (
    os.getenv(
        "ALLOW_DEMO_MODE",
        "true",
    ).lower()
    == "true"
)