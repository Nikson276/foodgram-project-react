from django.contrib import admin
from .models import (
    Tag, Ingredients, Ingredient,
    Recipe, Favorite, Shoplist
)


admin.site.register(Tag)
admin.site.register(Ingredients)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(Shoplist)
