from django.urls import path
from core.views import CreateTokenView

urlpatterns = [
    path('auth/token/', CreateTokenView.as_view(), name='token')
]
