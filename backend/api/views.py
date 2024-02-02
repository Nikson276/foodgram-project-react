from django.shortcuts import render
from rest_framework import viewsets
from users.models import User
from recipes.models import Tag, Ingredient, Recipe, Favorite, Follow, Shoplist
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer,
    RecipeSerializer, FollowSerializer, FavoriteSerializer,
    ShoplistSerializer
)


# app classes - users
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# app classes - recipes
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = RecipeSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = FollowSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = FavoriteSerializer


class ShoplistViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = ShoplistSerializer
