import requests
from attrs import define
from random import SystemRandom
from urllib.parse import urlencode
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET

from django.conf import settings
from django.urls import reverse_lazy
from django.core.exceptions import ImproperlyConfigured, ValidationError


@define
class GoogleLoginCredentials:
    client_id: str
    client_secret: str


@define
class GoogleTokens:
    id_token: str
    access_token: str


class GoogleLoginService:
    API_URI = reverse_lazy("google-callback")

    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    def __init__(self):
        self._credentials = get_google_login_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        rand = SystemRandom()
        return "".join(rand.choice(chars) for _ in range(length))

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        return f"{domain}{api_uri}"

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()
        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "prompt": "select_account",
            "access_type": "offline",
            "scope": " ".join(self.SCOPES),
            "state": state,
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_google_tokens(self, code):
        redirect_uri = self._get_redirect_uri()

        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ValidationError("Failed to obtain access token from Google.")

        tokens = response.json()
        return GoogleTokens(
            id_token=tokens["id_token"], access_token=tokens["access_token"]
        )

    def get_user_info(self, google_tokens):
        access_token = google_tokens.access_token

        response = requests.get(
            self.GOOGLE_USER_INFO_URL, params={"access_token": access_token}
        )

        if not response.ok:
            raise ValidationError("Failed to obtain user info from Google.")

        return response.json()


def get_google_login_credentials():
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    return GoogleLoginCredentials(client_id=client_id, client_secret=client_secret)
