import django_filters
from recipes.models import Recipe


class IsFavoriteFilter(django_filters.BooleanFilter):
    field_name = 'is_favorited'
    method = 'filter_by_is_favorited'

    def filter_by_is_favorited(self, queryset, name, value):
        print(f'ЧТО ТАМ В FAVORITE ____{value}')
        if value is not None:
            value = value.lower() == '1'  # Преобразуем строку в булево значение
            return [obj for obj in queryset if obj.is_favorited == value]
        return queryset


class RecipeViewSetFilter(django_filters.FilterSet):
    """ Класс для Фильтрации по Тегам на страницах"""
    is_favorited = IsFavoriteFilter()
    tags = django_filters.CharFilter(
        method='filter_tags'
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'tags']

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()
