from django.contrib import admin
from .models import (
    Tag, Ingredient, IngredientRecipe,
    Recipe, Favorite, Shoplist
)


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientRecipe)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(Shoplist)
