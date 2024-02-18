from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet, IngredientViewSet, RecipeViewSet,
    FollowViewSet, FavoriteViewSet, ShoppingListViewSet,
    CustomUserViewSet
)


# All url variants
# http://127.0.0.1:5500/api/users/
# http://127.0.0.1:5500/api/tags/
# http://127.0.0.1:5500/api/recipes/
# http://127.0.0.1:5500/api/recipes/download_shopping_cart/
# http://127.0.0.1:5500/api/recipes/{id}/shopping_cart/
# http://127.0.0.1:5500/api/recipes/{id}/favorite/
# http://127.0.0.1:5500/api/users/subscriptions/
# http://127.0.0.1:5500/api/users/{id}/subscribe/
# http://127.0.0.1:5500/api/ingredients/

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
