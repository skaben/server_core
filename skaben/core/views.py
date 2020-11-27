from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework import viewsets

from django.http import HttpResponse
from django.conf import settings


class CreateTokenView(ObtainAuthToken):
    """ Create a new auth token for user """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class DynamicAuthMixin:

    def get_authenticators(self, request, **kwargs):
        if settings.ENVIRONMENT in ("dev", "DEV"):
            return []
        return (TokenAuthentication,)

    def get_permissions(self, request, **kwargs):
        if settings.ENVIRONMENT in ("dev", "DEV"):
            return []
        return (IsAuthenticated,)


def login_view(request):
    html = """
    <html>
      <head>
        <title>login</title>
      </head>
      <body>
      permission denied.
      </body>
    </html>
    """

    return HttpResponse(html)
