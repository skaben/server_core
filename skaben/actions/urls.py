from django.urls import include, path
from eventlog import views
from rest_framework.routers import SimpleRouter

app_name = 'energystate'

router = SimpleRouter()
router.register('energystate', views.EnergyStateViewset)

urlpatterns = [
    path('', include(router.urls)),
]
