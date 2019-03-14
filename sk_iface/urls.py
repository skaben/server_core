from django.urls import path, include
from sk_iface import views

urlpatterns = [
    path('', views.index, name='index'),
]
