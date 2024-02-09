from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.permissions import CurrentUserOrAdmin
from users.models import User, Follow
from recipes.models import (
    Tag, Ingredient, IngredientRecipe,
    Recipe, Favorite, Shoplist
)
from .serializers import (
    IngredientRecipeSerializer, RecipeListSerializer, RecipeCreateSerializer,
    FollowSerializer, FavoriteSerializer, ShoplistSerializer,
    IngredientSerializer, TagSerializer
)
from .mixins import PermissionMixin


# app classes - users
class CustomUserViewSet(DjoserUserViewSet, PermissionMixin):
    queryset = User.objects.all()
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
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class IngredientRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecipe.objects.all()
    serializer_class = IngredientRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        else:
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoplistViewSet(viewsets.ModelViewSet):
    queryset = Shoplist.objects.all()
    serializer_class = ShoplistSerializer
