from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_AMOUNT = 1
MAX_AMOUNT = 32000
MIN_TIME_MINUTES = 1
MAX_TIME_MINUTE = 32000

User = get_user_model()


class Tag(models.Model):
    """ Теги """
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=16, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиентов."""
    name = models.CharField('Название', max_length=200, default='dummy')
    measurement_unit = models.CharField('ЕИ', max_length=15, default='г')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return ('{n} ({u})').format(n=self.name, u=self.measurement_unit)


class Recipe(models.Model):
    """ Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='images/',
        null=True,
        default=None
    )
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=MIN_TIME_MINUTES,
        validators=[
            MaxValueValidator(MAX_TIME_MINUTE),
            MinValueValidator(
                MIN_TIME_MINUTES,
                f'Время не может быть меньше {MIN_TIME_MINUTES}'
            )
        ],
        verbose_name='Время приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    @admin.display(
        description='Избранное (кол-во чел)',
    )
    def favorite_counter(self):
        """ Вывод в админку счетчик у рецепта"""
        return self.recipe_favorites.count()

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """ Модель связи рецепта и ингредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='rel_RecipeIngredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='rel_RecipeIngredient'
    )
    amount = models.PositiveSmallIntegerField(
        default=MIN_AMOUNT,
        validators=[
            MaxValueValidator(MAX_AMOUNT),
            MinValueValidator(
                MIN_AMOUNT,
                f'Кол-во не может быть менее {MIN_AMOUNT}'
            )
        ],
        verbose_name='Количество ингредиента',
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]

    def __str__(self):
        return self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users_favorite')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_favorites')

    class Meta:
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return self.user.username


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users_shoppinglist')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_shoppinglists')

    class Meta:
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shoppinglist'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return self.user.username
