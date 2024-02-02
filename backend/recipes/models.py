from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


# class Tag(models.Model):
#     title = models.CharField('Название', max_length=200)
#     color_code = models.CharField('цвет', max_length=16)
#     slug = models.SlugField(max_length=50, unique=True)

#     def __str__(self):
#         return self.title


# class Ingredient(models.Model):
#     title = models.CharField('Название', max_length=200)
#     quantity = models.DecimalField(
#         'Количество', max_digits=5, decimal_places=2, default=0
#         )
#     uom = models.SlugField('Единица измерения' ,max_length=50, unique=True)

#     def __str__(self):
#         return self.title


# class Recipe(models.Model):
#     user_id = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='author')    
#     name = models.TextField('Название')
#     image = models.ImageField(
#         upload_to='recipes/', null=True, blank=True)
#     text = models.TextField('Описание')
#     ingredient_id = models.ManyToManyField(Achievement,
#                                           through='AchievementCat')
#     tag = models.ForeignKey(
#         Tag, on_delete=models.SET_NULL,
#         related_name='recipes', blank=True, null=True
#     )
#     cook_time = models.DateTimeField('Дата публикации', auto_now_add=True)

#     def __str__(self):
#         return self.text


# class Follow(models.Model):
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='follower')
#     following = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='following')

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user', 'following'],
#                 name='unique_user_following'
#             )
#         ]


# class Favorite(models.Model):
#     author = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='comments')
#     post = models.ForeignKey(
#         Post, on_delete=models.CASCADE, related_name='comments')
#     text = models.TextField()
#     created = models.DateTimeField(
#         'Дата добавления', auto_now_add=True, db_index=True)