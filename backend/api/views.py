from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet as DjoserUserViewSet
from djoser.permissions import CurrentUserOrAdmin
from rest_framework import permissions
from users.models import User, Follow
from recipes.models import (
    Tag, Ingredient, RecipeIngredient,
    Recipe, Favorite, ShoppingList
)
from .serializers import (
    RecipeIngredientSerializer, RecipeListSerializer, RecipeCreateSerializer,
    FollowSerializer, FavoriteSerializer, ShoppingListSerializer,
    IngredientSerializer, TagSerializer, FollowReadListSerializer
)
from .mixins import (
    UserRecipeModelMixin, ShoppingListDownloadHelper, AuthorUserOrAdmin
)
from .filters import (
    RecipeViewSetFilter, RecipeCustomFilter, CustomSearchFilter
)
from foodgram.settings import ATTACHMENT_FORMAT


# app classes - users
class CustomUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    search_fields = ('username', 'email')
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        """ Переопределим полномочия в зависимости от действия"""
        if self.action == "me":
            self.permission_classes = [CurrentUserOrAdmin,]
        elif self.request.method in permissions.SAFE_METHODS:
            # allow GET, HEAD or OPTIONS requests
            self.permission_classes = [AllowAny,]
        else:
            self.permission_classes = [CurrentUserOrAdmin,]
        return super().get_permissions()

    @action(
            detail=False,
            methods=['get'],
            serializer_class=FollowReadListSerializer,
            permission_classes=[CurrentUserOrAdmin,],
            pagination_class=LimitOffsetPagination,
            url_path='subscriptions',
        )
    def subscriptions(self, request):
        """ Метод вывода списка подписок юзера"""
        user: User = request.user
        subscribtions: Follow = user.follower.all()
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
        user: User = request.user
        author: User = get_object_or_404(User, id=id)

        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'user': user.pk, 'following': author.pk},
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                    )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            subscription = get_object_or_404(
                Follow,
                user=user,
                following=author
            )
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
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer


class RecipeViewSet(
    viewsets.ModelViewSet,
    UserRecipeModelMixin,
    ShoppingListDownloadHelper,
    RecipeCustomFilter
):
    """ Обработка эндпоинта /recipes"""
    queryset = Recipe.objects.all()
    filterset_class = RecipeViewSetFilter

    def get_permissions(self):
        """ Переопределим полномочия в зависимости от действия"""
        if self.request.method in permissions.SAFE_METHODS:
            # allow GET, HEAD or OPTIONS requests
            self.permission_classes = [AllowAny,]
        else:
            self.permission_classes = [AuthorUserOrAdmin,]
        return super().get_permissions()

    def get_queryset(self):
        """ Добавим фильтр по Избранному, на уровне queryset"""
        query_params = self.request.query_params
        if query_params.get(self.FAVORITE_PARAM) is not None:
            queryset = self.get_filtered_queryset(
                query_param=self.FAVORITE_PARAM,
                user=self.request.user
            )
        elif query_params.get(self.SHOPPING_CART_PARAM) is not None:
            queryset = self.get_filtered_queryset(
                query_param=self.SHOPPING_CART_PARAM,
                user=self.request.user
            )
        else:
            queryset = super().get_queryset()
        return queryset

    def get_serializer_class(self):
        """ Определим какой сериализатор выдать"""
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        else:
            return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,],
            url_name='favorite'
    )
    def favorite(self, request, pk):
        """ Метод добавления/удаления рецепта в избранное"""
        model = Favorite
        serializer_class = FavoriteSerializer
        return self.add_delete_model_helper(
            model=model,
            serializer_class=serializer_class,
            request=request,
            pk=pk
        )

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated,],
            url_name='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        """ Метод добавления/удаления в список покупок"""
        model = ShoppingList
        serializer_class = ShoppingListSerializer
        return self.add_delete_model_helper(
            model=model,
            serializer_class=serializer_class,
            request=request,
            pk=pk
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """ Метод выгрузки списка продуктов"""
        user = request.user
        shopping_list = ShoppingList.objects.filter(
            user=user
        ).prefetch_related('recipe')

        final_list: dict = {}
        recipe_list: list = []
        # Сбор данных рецептов в список
        for item in shopping_list:
            ingredient_list = item.recipe.rel_RecipeIngredient.all()

            for position in ingredient_list:
                if position.ingredient in final_list:
                    final_list[position.ingredient] += position.amount
                else:
                    final_list[position.ingredient] = position.amount
            recipe_list.append(f'# {item.recipe.name}')

        return self.create_file_helper(
            file_format=ATTACHMENT_FORMAT,
            array1=recipe_list,
            array2=final_list
        )


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
