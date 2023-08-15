from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model

from recipes.models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели User
    '''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscribing.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Tag
    '''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Ingredient
    '''
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id')


class RecipeShortSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe (краткая версия):
    используется для представления рецепта вкратце
    '''
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели RecipeIngredient:
    используется как вложенный для RecipeSerializer
    '''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    # Проверка на заполнение поля 'amount' (количество ингредиента)
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Необходимо указать количество ингредиента')
        return value


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe
    '''
    author = UserSerializer(default=CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True, source='ingr_in_rec')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'name', 'text', 'image',
                  'cooking_time', 'id', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')

    # Методы для SerializerMethodField
    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()

    # Валидация:
    def validate(self, data):
        # Проверка на заполнение обязательных полей
        not_empty_checklist = {
            'image': 'Необходимо выбрать изображение для рецепта',
            'tags': 'Необходимо выбрать хотя бы 1 тег',
            'ingr_in_rec': 'Необходимо выбрать хотя бы 1 ингредиент'}
        for field in not_empty_checklist:
            if not data[field]:
                raise ValidationError(f'{not_empty_checklist[field]}')

        # Проверка "не повторяются ли ингредиенты внутри одного рецепта"
        ingredients_unique_checklist = []
        for ingredient in data['ingr_in_rec']:
            ingredients_unique_checklist.append(
                ingredient['ingredient']['id']
            )
        if len(ingredients_unique_checklist) != (
           len(set(ingredients_unique_checklist))):
            raise ValidationError('Ингредиенты не могут повторятся!')

        # Проверка поля 'cooking_time'
        if not (0 < data['cooking_time'] <= 1440):
            raise ValidationError(
                'Время приготовления должно быть в интревале'
                '1 минтуа - 1440 минут (1 день)'
            )
        return data


class RecipeWriteSerializer(RecipeSerializer):
    '''
    Сериализатор модели Recipe (для записи рецепта)
    '''
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    def set_ingredients(self, recipe, ingredients):
        '''
        Создает в БД объекты модели RecipeIngredient,
        т.е. записи об ингредиентах в рецепте и их количистве
        '''
        rec_ingr_list = [
            RecipeIngredient(
                ingredient=Ingredient.objects.get(
                    id=ingredient['ingredient']['id']),
                amount=ingredient['amount'],
                recipe=recipe,
            )
            for ingredient in ingredients
            ]
        RecipeIngredient.objects.bulk_create(rec_ingr_list)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingr_in_rec')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingr_in_rec')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.set_ingredients(instance, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance=instance, context=context).data


class SubscribtionsSerializer(UserSerializer):
    '''
    Сериализатор модели Subscribtions
    '''
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'recipes',
                  'last_name', 'is_subscribed', 'recipes_count', )

    # Методы для SerializerMethodField
    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = int(request.query_params.get('recipes_limit'))
        limited_recipes = obj.recipes.all()[:recipe_limit]
        return RecipeShortSerializer(
            limited_recipes, context=context, many=True).data
