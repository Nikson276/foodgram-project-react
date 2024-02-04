from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.permissions import CurrentUserOrAdmin
from foodgram.settings import DJOSER as settings
from users.models import User, Follow
from recipes.models import (
    Tag, Ingredients, Ingredient,
    Recipe, Favorite, Shoplist
)
from .serializers import (
    UserCreateSerializer, UserSetPassSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer, FollowSerializer,
    FavoriteSerializer, ShoplistSerializer, IngredientsSerializer
)
from .mixins import PermissionMixin


# app classes - users
class CustomUserViewSet(DjoserUserViewSet, PermissionMixin):
    queryset = User.objects.all()
    # serializer_class = UserCreateSerializer
    search_fields = ('username', 'email')
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny,]


    def get_permissions(self):
        """ Переопределим полномочия для ендпоинта /me"""
        if self.action == "me":
            self.permission_classes = [CurrentUserOrAdmin,]
        return super().get_permissions()

    
    # Если в запросе есть /subscriptions/, 
    # вызвать Follow.objects.filter по юзеру
    # TODO



# app classes - recipes
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoplistViewSet(viewsets.ModelViewSet):
    queryset = Shoplist.objects.all()
    serializer_class = ShoplistSerializer
