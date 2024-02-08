import base64
import webcolors
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    SetPasswordSerializer
    )
from django.core.files.base import ContentFile
from rest_framework import serializers
from users.models import User, Follow
from recipes.models import (
    Tag, Ingredient, IngredientRecipe,
    Recipe, Favorite, Shoplist
)


# image upload helper classes
class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


# app classes - users
class UserCreateSerializer(DjoserUserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'password', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        print(f'ЭТО РЕКВЕСТ____________{self.context["request"].user}')
        print(f'ЭТО ЮЗЕР_ИД____________{self.context["request"].user.id}')
        print(f'ОБЪЕКТ {obj}')

        subscribtions = Follow.objects.filter(
            user=self.context['request'].user.id
        )
        if subscribtions:
            print(f'ЭТО ПОДПИСКИ МОИ? {subscribtions}')
            subscribtions = subscribtions.following().filter(
                following=obj
            )
            if subscribtions:
                # Юзер найден в подписках
                return True
        return False


class UserSetPassSerializer(SetPasswordSerializer):

    class Meta:
        model = User
        fields = (
            'new_password', 'current_password'
        )


# app classes - recipes
class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        default=0.5
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeBaseSerializer(serializers.ModelSerializer):
    author = UserCreateSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=1)
    # is_favorite = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time'
            )


class RecipeListSerializer(RecipeBaseSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time'
            )


class RecipeCreateSerializer(RecipeBaseSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
            )

    def create(self, validated_data):
        # убираем ингредиенты и теги из словаря
        ingredients_data = validated_data.pop('ingredients')
        # tags_data = validated_data.pop('tags')
        # создаем пустой рецепт без них
        recipe = Recipe.objects.create(**validated_data)

        # создаем связи рецепт-ингредиент
        create_ingredients = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        ]

        # создаем связи с тегами
        # create_tags = [
        #     TagRecipe(
        #         recipe=recipe,
        #         tag=tag
        #     )
        #     for tag in tags_data
        # ]

        IngredientRecipe.objects.bulk_create(create_ingredients)
        # TagRecipe.objects.bulk_create(create_tags)

        return recipe

class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        fields = ('id', 'user', 'following')
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


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=True
    )
    
    class Meta:
        fields = ('id', 'user', 'recipe')
        model = Favorite

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Такой рецепт уже в избранном!'
            )
        ]


class ShoplistSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=True
    )
    
    class Meta:
        fields = ('id', 'user', 'recipe')
        model = Shoplist

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Shoplist.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок!'
            )
        ]