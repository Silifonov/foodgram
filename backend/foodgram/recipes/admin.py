from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart,
    Subscriptions
)


# Классы "inline" для отображения свзанных моделей в
# разделе админ-зоны "Рецепты"
class IngredientInline(admin.TabularInline):
    model = Ingredient.recipes.through


class FavoriteInline(admin.TabularInline):
    model = Favorite


class ShoppingCartInline(admin.TabularInline):
    model = ShoppingCart


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'favorite_counter')
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Добавлений в избранное')
    def favorite_counter(self, obj):
        return obj.in_favorite.count()

    inlines = (
        IngredientInline,
        FavoriteInline,
        ShoppingCartInline
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
