from django.conf.urls import url
from django.urls import path, include
#from .urlrest import router  # separated REST urls
from rest_framework import routers, generics
from .views import LockViewSet, TerminalViewSet, ExampleView, LockPartialUpdate

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

# actual urls
router.register(r'lock', LockViewSet)
router.register(r'term', TerminalViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'test-view/', ExampleView.as_view()),
    url(r'^lock/update-partial/(?P<pk>\d+)/$',
        LockPartialUpdate.as_view(), name='lock_partial_update'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
]