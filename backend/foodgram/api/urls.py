from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet,
    RecipeViewSet,
    IngredientViewSet,
    CustomUserViewSet
)

app_name = 'api'


router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
