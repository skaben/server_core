from django.urls import path, include
from rest_framework.routers import SimpleRouter

from assets import views

app_name = 'assets'

router = SimpleRouter()
router.register('userinput', views.UserInputViewSet)
router.register('textfile', views.TextFileViewSet)
router.register('imagefile', views.ImageFileViewSet)
router.register('audiofile', views.AudioFileViewSet)
router.register('videofile', views.VideoFileViewSet)
router.register('menuitem', views.MenuItemViewSet)
router.register('workmode', views.WorkModeViewSet)
router.register('hackgame', views.HackGameViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
