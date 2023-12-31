from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user(scope):
    headers = dict(scope["headers"])
    if b"authorization" in headers:
        try:
            (header_type, key) = headers[b"authorization"].decode().split()
            if header_type == "Token":
                token = Token.objects.get(key=key)
                return token.user
        except:
            return AnonymousUser()

    return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = await get_user(scope)
        return await self.app(scope, receive, send)
