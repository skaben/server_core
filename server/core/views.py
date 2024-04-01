from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings


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
        <title>SKABEN - Permission denied</title>
      </head>
      <body>
      Permission denied.
      </body>
    </html>
    """

    return HttpResponse(html)


def health_check(request):
    module = request.GET.get('module')

    result = {
        "status": "healthy"
    }

    if module == 'workers':
        result = {}

    return JsonResponse(result)
