import csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from recipes.models import Recipe, RecipeIngredient
from typing import Optional
from django.http import Http404
from rest_framework.exceptions import APIException


class AuthorUserOrAdmin(permissions.IsAuthenticated):
    """ Class for custom permission """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.author_id == user.id


class ObjectNotFound(APIException):
    """ Class helper with exceptions 400"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Объект не найден'
    default_code = 'Not found'


class UserRelatedModelMixin:
    """
    Class helper for working with related models
    to user
    """
    def get_or_400(self, model_or_qs, **kwargs):
        try:
            return get_object_or_404(model_or_qs, **kwargs)
        except Http404:
            raise ObjectNotFound

    def add_delete_model_helper(
        self,
        par_model,
        rel_model,
        rel_name,
        serializer_class,
        request,
        pk
    ):
        """ Helper method to add/delete obj to model"""

        user: Optional[User] = request.user
        parent_obj = get_object_or_404(par_model, id=pk)

        if request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.pk, rel_name: parent_obj.pk},
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # DELETE
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


class ShoppingListDownloadHelper:
    """ Class helper to implement file download in diff format"""
    def create_csv(self, array1: list, array2: dict) -> HttpResponse:
        """ Создание .csv файла """

        filename = 'shopping_list.csv'
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="{0}"'.format(filename)

        writer = csv.writer(response)
        # Устанавливаем кодировку UTF-8 для файла .csv
        # Добавляем BOM для корректного отображения в Excel
        response.write(u'\ufeff'.encode('utf8'))

        writer.writerow(['Список рецептов:'])
        writer.writerow([array1])
        writer.writerow([' '])
        writer.writerow(['ИТОГО Список покупок:'])
        for pos, amount in array2.items():
            writer.writerow([f'{pos} --- {amount}'])

        return response

    def create_pdf(self, array1: list, array2: dict) -> HttpResponse:
        """ Создание .pdf файла """
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.pdf"'

        # Генерация содержимого PDF
        p = canvas.Canvas(response)
        # Устанавливаем шрифт и кодировку для кириллицы
        pdfmetrics.registerFont(TTFont('Arial', './static/fonts/Arial.ttf'))
        p.setFont('Arial', 12)

        p.drawString(100, 800, "Список рецептов:")
        y = 780
        for recipe in array1:
            p.drawString(100, y, recipe)
            y -= 20
        y -= 10
        p.line(100, y, 300, y)
        y -= 30
        p.drawString(100, y, "Список продуктов:")
        y -= 20
        for pos, amount in array2.items():
            ingredient = f'{pos} --- {amount}'
            p.drawString(100, y, ingredient)
            y -= 20
        p.showPage()
        p.save()

        return response

    def create_file_helper(
        self, file_format, array1: list, array2: dict
    ) -> HttpResponse:
        """ Медот для создания файла выгрузки в нужном формате"""
        if file_format == 'csv':
            # Создание .csv файла:
            return self.create_csv(array1=array1, array2=array2)

        elif file_format == 'pdf':
            # Создание PDF-файла
            return self.create_pdf(array1=array1, array2=array2)
        return Response(
            'ATTACHMENT_FORMAT_ERROR Please contact your administrator',
            status=status.HTTP_400_BAD_REQUEST
        )


class RecipeRelationHelper:
    """ Class helper to create new relations
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
