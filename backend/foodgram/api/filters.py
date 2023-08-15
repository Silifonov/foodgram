from django_filters.rest_framework import (
    FilterSet,
    BooleanFilter,
    ModelMultipleChoiceFilter,
    CharFilter
)
from recipes.models import (
    Tag,
    Recipe,
    Ingredient
)


class RecipesFilter(FilterSet):
    '''
    Фильтр рецептов
    '''
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            filtered_queryset = queryset.filter(in_favorite__user=user)
            return filtered_queryset
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            filtered_queryset = queryset.filter(in_shopping_cart__user=user)
            return filtered_queryset
        return queryset


class IngredientSearchFilter(FilterSet):
    '''
    Фильтр для поиска ингредиентов
    '''
    name = CharFilter(field_name='name', method='search_ingredient')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_ingredient(self, queryset, name, value):
        if value:
            low_case_value = value.lower()
            filtered_queryset = queryset.filter(
                name__startswith=low_case_value
            )
            return filtered_queryset
