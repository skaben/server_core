from django.urls import path, include
from rest_framework.routers import SimpleRouter

from menu_item import views

app_name = 'menu_item'

router = SimpleRouter()
router.register('menu_item', views.MenuItemViewSet)
router.register('work_mode', views.WorkModeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
