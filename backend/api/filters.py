import django_filters
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
        fields = ['tags']


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
