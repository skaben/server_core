from django.urls import include, path
from actions import views
from rest_framework.routers import SimpleRouter

app_name = 'actions'

router = SimpleRouter()
router.register('energystate', views.EnergyStateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
