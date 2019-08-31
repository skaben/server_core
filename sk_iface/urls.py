from django.urls import path, include
from django.conf.urls import url
from rest_framework import routers
from sk_iface import views, viewsets

#state_mgmt = viewsets.StateViewSet.as_view({
#    'get': 'list',
#    'post': 'set_current'
#})

router = routers.DefaultRouter()

# register API urls
router.register(r'api/state', viewsets.StateViewSet)
router.register(r'api/locks', viewsets.LockViewSet)
router.register(r'api/terms', viewsets.TerminalViewSet)
router.register(r'api/cards', viewsets.CardViewSet)
router.register(r'api/values', viewsets.ValueViewSet)
router.register(r'api/permissions', viewsets.PermissionViewSet)
router.register(r'api/texts', viewsets.InfoTextViewSet)
router.register(r'api/menus', viewsets.MenuItemViewSet)

urlpatterns = [
    path('',
         views.index,
         name='index'),
    path('', include(router.urls)),
    path('log',
         views.log,
         name='log-records'),
    path('sendlog',
         views.sendlog,
         name='sendlog'),
    path('^state/update/$',
         views.change_state,
         name='update-alert'),
    path('^dev/lock/(?P<pk>[-\w]+)/update/$',
         views.lock,
         name='update-lock'),
    path('^dev/term/(?P<pk>[-\w]+)/update/$',
         views.terminal,
         name='update-terminal'),
]

