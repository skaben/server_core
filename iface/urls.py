from django.conf.urls import url
from django.urls import path, include
from .urlrest import router  # separated REST urls
from iface import views

urlpatterns = [
    path('', views.index, name='index'),
    #
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]