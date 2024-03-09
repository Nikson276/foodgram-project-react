import base64

import webcolors
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer
from djoser.serializers import \
    UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from rest_framework import serializers
from rest_framework.utils import model_meta
from users.models import Follow, User

from .mixins import RecipeRelationHelper
from .validators import RecipeCreateValidation


class Hex2NameColor(serializers.Field):
    """ Преобразование hex цветов в имя"""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    """ Декодирование бинарника картинок """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


# app classes - users
class CustomUserCreateSerializer(DjoserUserCreateSerializer):
    """ Создание или изменение юзера"""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'password',
        )


class UserListSerializer(DjoserUserSerializer):
    """ Чтение данных юзера"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        )
        read_only_fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
        )

    def get_is_subscribed(self, obj):
        """ Метод для поля в ответе Подписан я или нет"""

        view = self.context.get('view')
        if view is not None:
            if view.action == 'me':
                return False
        request = self.context.get('request')
        get_subscribtions = self.context.get('subscribtions')

        if get_subscribtions:
            # from subscribtions endpoint, always True
            return True
        return (request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user,
                    following=obj
                ).exists()
                )


class UserSetPassSerializer(SetPasswordSerializer):
    """ Смена пароля у юзера"""

    class Meta:
        model = User
        fields = (
            'new_password', 'current_password'
        )


# app classes - recipes
class TagSerializer(serializers.ModelSerializer):
    """ Теги """

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """ Ингредиенты справочник"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """ Добавление ингредиента в рецепта"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0.5
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ReadRecipeIngredientSerializer(serializers.ModelSerializer):
    """ Рендер ингредиента в рецепт"""
    name = serializers.CharField(
        source="ingredient.name",
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
        read_only=True
    )
    amount = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0.5,
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id',)


class RecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для возврата списка или рецепта"""
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserListSerializer(
        read_only=True
    )
    ingredients = ReadRecipeIngredientSerializer(
        source='rel_RecipeIngredient',
        many=True,
    )
    image = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        many_to_many = 'tags'
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'name', 'text', 'cooking_time')

    def is_model_instance_exist(self, obj, model):
        """ Метод хелпер - находится ли в модели объект """
        request = self.context.get('request')
        return model.objects.filter(
            user=request.user.pk,
            recipe=obj.pk
        ).exists()

    def get_is_favorited(self, obj):
        """ Находится ли в избранном """
        return self.is_model_instance_exist(obj=obj, model=Favorite)

    def get_is_in_shopping_cart(self, obj):
        """ Находится ли в списке покупок """
        return self.is_model_instance_exist(obj=obj, model=ShoppingList)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RecipeShortListSerializer(serializers.ModelSerializer):
    """ Сериализатор для возврата короткой инфы о рецепте"""

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class RecipeCreateSerializer(
    serializers.ModelSerializer,
    RecipeRelationHelper,
    RecipeCreateValidation
):
    """ Сериализатор создания рецепта"""
    author = UserListSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField(
        required=True,
        allow_null=True)
    cooking_time = serializers.IntegerField(
        min_value=1,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        error_message = self.run_custom_validation(attrs)
        if error_message:
            raise serializers.ValidationError(
                {"message": error_message}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        # убираем ингредиенты и теги из словаря
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        # создаем пустой рецепт без них
        recipe = Recipe.objects.create(**validated_data)

        return self.create_ingredient_tags_recipe(
            recipe,
            ingredients_data,
            tags_data
        )

    def update(self, instance, validated_data):
        """ Метод обновления рецепта """

        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                if attr == 'ingredients':
                    ingredients_data = value
                elif attr == 'tags':
                    tags_data = value
            else:
                setattr(instance, attr, value)

        instance.save()
        instance.rel_RecipeIngredient.all().delete()
        field = getattr(instance, 'tags')
        field.clear()

        return self.create_ingredient_tags_recipe(
            instance,
            ingredients_data,
            tags_data
        )

    def to_representation(self, instance):
        return RecipeListSerializer(
            context=self.context,
            instance=instance
        ).data


class FollowReadListSerializer(UserListSerializer):
    """ Подписки с рецептами пользователя"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        )

    def get_recipes(self, obj):
        """" Чтение всех рецептов юзера, с учетом лимита (если есть)"""
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]

        serializer = RecipeShortListSerializer(
            recipes,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """ Счетчик кол-ва рецептов юзера"""
        return obj.recipes.all().count()


class FollowSerializer(serializers.ModelSerializer):
    """ Подписки создание"""

    class Meta:
        fields = ('user', 'following')
        model = Follow

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Такая подписка уже существует!'
            )
        ]

    def validate(self, attrs):
        if self.context['request'].user == attrs['following']:
            raise serializers.ValidationError(
                {"message": "Нельзя подписаться на себя!"}
            )
        return super().validate(attrs)

    def to_representation(self, instance):

        return FollowReadListSerializer(
            context=self.context,
            instance=instance.following
        ).data


class FavoriteReadListSerializer(RecipeShortListSerializer):
    """ Отображение избранного
    Полностью наследует все из Рецептов.
    """
    pass


class FavoriteSerializer(serializers.ModelSerializer):
    """ Списоr избранное создание/удаление """

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Такой рецепт уже в избранном!'
            )
        ]

    def to_representation(self, instance):

        return FavoriteReadListSerializer(
            context=self.context,
            instance=instance.recipe
        ).data


class ShoppingReadListSerializer(RecipeShortListSerializer):
    """ Отображение списка покупок
    Полностью наследует все из Рецептов.
    """
    pass


class ShoppingListSerializer(serializers.ModelSerializer):
    """ Список покупок добавление/удаление """

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingList

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Такой рецепт уже в списке покупок!'
            )
        ]

    def to_representation(self, instance):

        return ShoppingReadListSerializer(
            context=self.context,
            instance=instance.recipe
        ).data
