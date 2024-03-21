from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """"Кастомный класс пользователя"""
    first_name = models.CharField(('first name'), max_length=150)
    last_name = models.CharField(('last name'), max_length=150)
    email = models.EmailField(('email address'), unique=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return self.user.username
