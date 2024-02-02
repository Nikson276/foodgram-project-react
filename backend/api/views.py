from django.shortcuts import render
from rest_framework import viewsets
from users.models import User, Follow
from recipes.models import (
    Tag, Ingredients, Ingredient,
    Recipe, Favorite, Shoplist
)
from .serializers import (
    UserSerializer, TagSerializer, IngredientSerializer,
    RecipeSerializer, FollowSerializer, FavoriteSerializer,
    ShoplistSerializer, IngredientsSerializer
)


# app classes - users
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Если в запросе есть /subscriptions/, вызвать Follow.objects.filter по юзеру


# app classes - recipes
class TagViewSet(viewsets.ModelViewSet):
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
