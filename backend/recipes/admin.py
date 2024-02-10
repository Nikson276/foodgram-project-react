from django.contrib import admin
from .models import (
    Tag, Ingredient, IngredientRecipe,
    Recipe, Favorite, Shoplist
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(Shoplist)

admin.site.empty_value_display = 'Не задано'