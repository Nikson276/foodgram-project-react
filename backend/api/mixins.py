from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .exception import ObjectNotFound
from recipes.models import Recipe, RecipeIngredient
from users.models import User


class UserRelatedModelMixin:
    """
    Class helper for working with related models
    to user
    """
    def get_or_400(self, model_or_qs, **kwargs):
        obj = model_or_qs.objects.filter(**kwargs).first()
        if obj is None:
            raise ObjectNotFound
        return obj

    def add_model(
        self,
        par_model: models.Model,
        rel_model: models.Model,
        rel_name: str,
        serializer_class: serializers.ModelSerializer,
        request: HttpRequest,
        pk: int
    ):
        """ Helper method to add obj to model"""

        user: Optional[User] = request.user
        parent_obj = get_object_or_404(par_model, id=pk)

        serializer = serializer_class(
            data={'user': user.pk, rel_name: parent_obj.pk},
            context={'request': request}
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as exc:
            return Response(
                exc.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete_model(
        self,
        par_model: models.Model,
        rel_model: models.Model,
        rel_name: str,
        serializer_class: serializers.ModelSerializer,
        request: HttpRequest,
        pk: int
    ):
        """ Helper method to delete obj to model"""

        user: Optional[User] = request.user
        parent_obj = get_object_or_404(par_model, id=pk)

        if isinstance(parent_obj, Recipe):
            model_obj = self.get_or_400(
                rel_model,
                user=user,
                recipe=parent_obj
            )
        elif isinstance(parent_obj, User):
            model_obj = self.get_or_400(
                rel_model,
                user=user,
                following=parent_obj
            )
        else:
            return Response(
                'Not implemented parent model',
                status=status.HTTP_400_BAD_REQUEST
            )
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeRelationMixin:
    """ Class mixin to create new relations
    between Recipe and Tags and Ingredients
    """

    def create_ingredient_tags_recipe(
        self,
        instance: Optional[Recipe],
        ingredients_data: dict,
        tags_data: dict
    ) -> Optional[Recipe]:

        # создаем связи рецепт-ингредиент
        create_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)

        # создаем связи рецепт теги
        for tag_id in tags_data:
            instance.tags.add(tag_id)

        return instance


class RecipeCreateValidationMixin:
    """ Class mixin to custom validation"""
    error_message: Optional[str] = None

    def run_custom_validation(self, attrs: dict) -> Optional[str]:
        """ Реализация дополнительной валидации ингредиентов и тегов"""
        if not attrs.get('ingredients'):
            self.error_message = 'Ингредиенты не переданы'
        else:
            ingredients_list: list = []
            for ingredient in attrs['ingredients']:
                ingredients_list.append(ingredient['id'])

            if (len(ingredients_list) > 0
                    and len(ingredients_list) != len(set(ingredients_list))):
                self.error_message = 'Ингредиенты повторяются'

        if self.error_message:
            return self.error_message

        if not attrs.get('tags'):
            self.error_message = 'Теги не переданы'
        else:
            tags_list = [tag.id for tag in attrs['tags']]
            if len(tags_list) != len(set(tags_list)):
                self.error_message = 'Теги повторяются'

        if self.error_message:
            return self.error_message
