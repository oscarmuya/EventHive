from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser


class StatelessUser(AnonymousUser):
    """
    A simple user class that is always anonymous but can hold
    the decoded token payload.
    """

    def __init__(self, token_payload):
        self.token_payload = token_payload

    @property
    def is_authenticated(self):
        return True  # The user is "authenticated" because the token was valid


class StatelessJWTAuthentication(JWTAuthentication):
    """
    An authentication class that only validates the JWT and does not
    perform a database lookup for the user.
    """

    def get_user(self, validated_token):
        # Instead of fetching a user from the DB, create a stateless user
        # containing the token's payload.
        return StatelessUser(validated_token)
