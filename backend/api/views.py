from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    IngredientSerializer, TagSerializer, FollowReadListSerializer
)
from .mixins import PermissionMixin


# app classes - users
class CustomUserViewSet(DjoserUserViewSet, PermissionMixin):
    queryset = User.objects.all()
    search_fields = ('username', 'email')
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        """ Переопределим полномочия для ендпоинта /me"""
        if self.action == "me":
            self.permission_classes = [CurrentUserOrAdmin,]
        return super().get_permissions()

    @action(
            detail=False,
            methods=['get'],
            serializer_class=FollowReadListSerializer,
            permission_classes=[CurrentUserOrAdmin,],
            pagination_class=LimitOffsetPagination,
            url_path='subscribtions',
        )
    def subscribtions(self, request):
        """ Метод вывода списка подписок юзера"""
        user: User() = request.user
        subscribtions: Follow() = user.follower.all()
        user_list = [follow_obj.following.id for follow_obj in subscribtions]

        # Создадим кверисет, с объектами модели Юзера, для всех подписок.
        queryset = User.objects.filter(pk__in=user_list)

        page = self.paginate_queryset(queryset)
        context = {
            'request': request,
            'subscribtions': True
        }
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,],
            url_name='subscribe',
        )
    def subscribe(self, request, id):
        """ Метод для создание и удаления подписки на юзера по ид"""
        user: User() = request.user
        author: User() = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': user.pk, 'following': author.pk},
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            subscription = get_object_or_404(Follow, user=user, following=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
