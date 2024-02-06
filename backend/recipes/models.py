from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    color = models.CharField('Цвет', max_length=16, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('ЕИ', max_length=4)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.DecimalField(
        'Количество',
        max_digits=5,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return self.ingredient.name


class Recipe(models.Model):
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
        verbose_name='Ингредиенты',
        related_name='ingredients'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
    )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users_favorite')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
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
