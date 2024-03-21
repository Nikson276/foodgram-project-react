import django_filters
from django.db.models import Q
from rest_framework import filters

from recipes.models import Recipe


class RecipeViewSetFilter(django_filters.FilterSet):
    """ Класс для Фильтрации по Тегам на страницах"""

    tags = django_filters.CharFilter(
        method='filter_tags'
    )

    def filter_tags(self, queryset, name, value):
        """ Метод фильтрации по тегам в параметрах запроса"""
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    class Meta:
        model = Recipe
        fields = ['author', 'tags']


class RecipeCustomFilter():
    """ Дополнительная фильтрация исходнго queryset модели Recipe"""
    FAVORITE_PARAM = 'is_favorited'
    SHOPPING_CART_PARAM = 'is_in_shopping_cart'

    def get_filtered_queryset(self, query_param, user):
        """ Фильтруем queryset по переданному параметру"""
        if query_param == self.FAVORITE_PARAM:
            param_queryset = user.users_favorite.all()
        elif query_param == self.SHOPPING_CART_PARAM:
            param_queryset = user.users_shoppinglist.all()

        param_list = [
            param['recipe_id']
            for param in param_queryset.values()
        ]
        return Recipe.objects.filter(pk__in=param_list)


class CustomSearchFilter(filters.SearchFilter):
    """ Хелпер для поиска по ингредиентам"""
    search_param = "name"

    def filter_queryset(self, request, queryset, view):
        search_param = request.query_params.get(
            self.search_param, ''
        ).lower()

        startswith_results = queryset.filter(
            name__istartswith=search_param
        )
        contains_results = queryset.filter(
            ~Q(name__istartswith=search_param),
            name__icontains=search_param
        )

        return startswith_results | contains_results
