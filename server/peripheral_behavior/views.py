from rest_framework import viewsets

from .models import MenuItem

from .serializers.menu import MenuPolymorphicSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuPolymorphicSerializer
