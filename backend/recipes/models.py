from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Название', max_length=200)
    color = models.CharField('Цвет', max_length=16)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('ЕИ', max_length=4)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    ingredient = models.OneToOneField(
        Ingredients,
        on_delete=models.CASCADE,
        blank=True, null=True
        )
    amount = models.DecimalField(
        'Количество', max_digits=5, decimal_places=2, default=0
        )

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField('Название', max_length=200)
    image = models.ImageField(
        upload_to='recipes/images',
        null=True,
        default=None
        )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)
    cooking_time = models.DateTimeField(
        'Время приготовления',
        auto_now_add=True
        )

    def __str__(self):
        return self.title


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'following_id'],
                name='unique_user_following'
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
