from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import CustomPagination
from .filters import RecipesFilter, IngredientSearchFilter
from .permissions import IsAuthorOrReadOnly
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingCart,
    Favorite,
    Subscriptions
)
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeWriteSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    SubscribtionsSerializer,
    UserSerializer,
    RecipeIngredient
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('subscribe', 'subscriptions'):
            return SubscribtionsSerializer
        if self.action in ('me', 'get', 'list', 'retrieve'):
            return UserSerializer
        return super().get_serializer_class()

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        id = kwargs.get('id')
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response(
                    {'error': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscribed, created = Subscriptions.objects.get_or_create(
                user=user, author=author)
            if not created:
                return Response(status=status.HTTP_409_CONFLICT)
            serializer = self.get_serializer(author)
            return Response(serializer.data)

        if request.method == 'DELETE':
            subscribed = get_object_or_404(
                Subscriptions, user=user, author=author)
            subscribed.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        user = request.user
        subscribtions = User.objects.filter(subscribed__user=user)
        serializer = self.get_serializer(subscribtions, many=True)
        queryset = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(queryset)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = RecipesFilter
    ordering = ('-created',)

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeShortSerializer
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeWriteSerializer

    def add_recipe(self, Model, recipe, user):
        '''
        Функция добавления рецепта,
        для actions favorite и shopping_cart
        '''
        interesting_recipe, created = Model.objects.get_or_create(
            user=user, recipe=recipe)
        if not created:
            return Response(status=status.HTTP_409_CONFLICT)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    def delete_recipe(self, Model, recipe, user):
        '''
        Функция удаления рецепта,
        для actions favorite и shopping_cart
        '''
        waste_recipe = get_object_or_404(Model, user=user, recipe=recipe)
        waste_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            return self.add_recipe(Favorite, recipe, user)
        return self.delete_recipe(Favorite, recipe, user)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, recipe, user)
        return self.delete_recipe(ShoppingCart, recipe, user)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').annotate(
            total_amount=Sum("amount"))
        shopping_list = [
            " | ".join(map(str, string.values())) for string in shopping_cart
        ]
        shopping_list_file = "\n".join(map(str, shopping_list))
        response = HttpResponse(shopping_list_file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
