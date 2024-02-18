from django.contrib import admin
from .models import (
    Tag, Ingredient, RecipeIngredient,
    Recipe, Favorite, ShoppingList
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_counter')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingList)

admin.site.empty_value_display = 'Не задано'