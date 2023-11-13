import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GOOGLE_OAUTH2_CLIENT_ID = os.environ.get("DJANGO_GOOGLE_OAUTH2_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get("DJANGO_GOOGLE_OAUTH2_CLIENT_SECRET")
GOOGLE_OAUTH2_PROJECT_ID = os.environ.get("DJANGO_GOOGLE_OAUTH2_PROJECT_ID")
