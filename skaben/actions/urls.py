from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ActionViewSet, UserInputViewSet

app_name = 'actions'

router = SimpleRouter()
router.register('user_input', UserInputViewSet)
router.register('action', ActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]