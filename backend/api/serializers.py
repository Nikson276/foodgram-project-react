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
    Tag, Ingredients, Ingredient,
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


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        required=True,
        many=True
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientSerializer(required=True, many=True)
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='slug',
        required=True,
        many=True
    )
    image = Base64ImageField(required=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        fields = (
            'id', 'author', 'name', 'image', 'text', 'ingredients',
            'tags', 'cooking_time'
            )
        model = Recipe
        read_only_fields = ('author',)


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