from django.urls import path, include
from sk_iface import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log', views.log, name='log-records'),
    path('sendlog', views.sendlog, name='sendlog'),
    path('^state/update/$', views.change_state, name='update-alert'),
    path('^dev/lock/(?P<pk>[-\w]+)/update/$',
         views.lock,
         name='update-lock'),
    path('^dev/term/(?P<pk>[-\w]+)/update/$',
         views.terminal,
         name='update-terminal'),
]

