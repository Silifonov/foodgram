from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField
from .validators import validate_amount

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=15,
        verbose_name='Тег'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='в минутах',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(1440)
        )
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self):
        return f'{self.name} (автор {self.author})'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='rec_with_ingr',
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingr_in_rec',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.FloatField(
        verbose_name='Количество',
        validators=(validate_amount,)
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.ingredient} - {self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favorite',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='favorite',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.user}'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe} - {self.user}'


class Subscriptions(models.Model):
    author = models.ForeignKey(
        User,
        related_name='subscribed',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            )
        ]
