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
class UserCreateSerializer(DjoserUserCreateSerializer):
    """ Создание нового юзера"""
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


class IngredientRecipeSerializer(serializers.ModelSerializer):
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
        model = IngredientRecipe
        fields = ('id', 'amount')


class ReadIngredientRecipeSerializer(serializers.ModelSerializer):
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
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id',)


class RecipeListSerializer(serializers.ModelSerializer):
    """ Сериализатор для возврата списка или рецепта"""
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    author = UserCreateSerializer(
        read_only=True
    )
    ingredients = ReadIngredientRecipeSerializer(
        source='rel_IngredientRecipe',
        many=True,
    )
    # TODO
    # is_favorite = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        many_to_many = 'tags'
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
            )
        read_only_fields = ('id', 'name', 'image', 'text', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор создания рецепта"""
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
    image = Base64ImageField(required=False) # TODO убери false
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
            )

    def create(self, validated_data):
        # убираем ингредиенты и теги из словаря
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
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
        IngredientRecipe.objects.bulk_create(create_ingredients)

        # создаем связи рецепт теги
        for tag_id in tags_data:
            recipe.tags.add(tag_id)

        return recipe

    def to_representation(self, instance):
        data = RecipeListSerializer(context=self.context, instance=instance).data
        return data


class FollowSerializer(serializers.ModelSerializer):
    """ Подписки """
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
    """ Списко избранное"""
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
    """ Корзина список покупок"""
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