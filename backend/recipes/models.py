from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=16, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингредиентов."""
    name = models.CharField('Название', max_length=200, default='dummy')
    measurement_unit = models.CharField('ЕИ', max_length=4, default='г')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель рецепта"""    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        upload_to='recipes/images',
        null=True,
        default=None
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
    )

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """ Модель связи рецепта и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='rel_IngredientRecipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='rel_IngredientRecipe'
    )
    amount = models.DecimalField(
        verbose_name='Количество ингредиента',
        max_digits=5,
        decimal_places=1,
        default=1,
        validators=[MinValueValidator(1, 'Кол-во не может быть менее 0.5')],
    )

    def __str__(self):
        return self.ingredient.name

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users_favorite')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite'
            )
        ]


class Shoplist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shoplist')
    recipe = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users_shoplist')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shoplist'
            )
        ]
