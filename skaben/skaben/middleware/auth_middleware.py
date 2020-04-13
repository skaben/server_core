from django.http import HttpResponse


class AuthRequiredMiddleware(object):

    allowed = (
        '/auth/token',
        '/favicon'
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        #if not request.path_info.startswith(self.allowed) and not request.user.is_authenticated:
        #    return HttpResponse("Unauthorized", status=401)
        return response
