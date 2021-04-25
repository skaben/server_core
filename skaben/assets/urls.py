from assets import views
from django.urls import include, path
from rest_framework.routers import SimpleRouter

app_name = 'assets'

router = SimpleRouter()
router.register('userinput', views.UserInputViewSet)
router.register('textfile', views.TextFileViewSet)
router.register('imagefile', views.ImageFileViewSet)
router.register('audiofile', views.AudioFileViewSet)
router.register('videofile', views.VideoFileViewSet)
router.register('hackgame', views.HackGameViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
