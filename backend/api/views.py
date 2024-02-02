from django.shortcuts import render
from rest_framework import viewsets
from users.models import User
from recipes.models import Tag, Ingredient, Recipe, Favorite, Follow, Shoplist
from .serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
