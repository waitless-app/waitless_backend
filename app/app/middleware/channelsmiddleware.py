from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    custom middleware
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)


class TokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        query_string = parse_qs(self.scope["query_string"].decode())
        token = query_string.get('token')
        if not token:
            self.scope['user'] = AnonymousUser()
            inner = self.inner(self.scope)
            return await inner(receive, send)
        try:
            UntypedToken(token[0])
        except (InvalidToken, TokenError):
            self.scope['user'] = AnonymousUser()
            inner = self.inner(self.scope)
            return await inner(receive, send)
        else:
            decoded_data = jwt_decode(
                token[0], settings.SECRET_KEY, algorithms=["HS256"])
            self.scope['user'] = await get_user(decoded_data["user_id"])
            inner = self.inner(self.scope)
            return await inner(receive, send)


def TokenAuthMiddlewareStack(inner): return TokenAuthMiddleware(
    AuthMiddlewareStack(inner))
