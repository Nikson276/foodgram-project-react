import csv
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from recipes.models import Recipe, IngredientRecipe
from typing import Optional


class PermissionMixin:
    """ Class for custom permission """

    def check_auth_permision(self):
        """ Check if user is authorized or raise exception"""
        if self.request.user.id is None:
            raise AuthenticationFailed(
                {"detail": "Учетные данные не были предоставлены."}
            )

    def check_author_permision(self):
        """ Check if user is author or raise exception"""
        obj = self.get_object()
        if self.request.user != obj.author:
            raise PermissionDenied({"message": "You don't have permission"})


class UserRecipeModelMixin:
    """
    Class helper for working with related models
    to user and recipe model
    """

    def add_delete_model_helper(self, model, serializer_class, request, pk):
        """ Helper method to add/delete obj to model"""

        user: Optional[User] = request.user
        recipe: Optional[Recipe] = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.pk, 'recipe': recipe.pk},
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
            model_obj = get_object_or_404(model, user=user, recipe=recipe)
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
        pdfmetrics.registerFont(TTFont('Arial', './fonts/Arial.ttf'))
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
            IngredientRecipe(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(create_ingredients)

        # создаем связи рецепт теги
        for tag_id in tags_data:
            instance.tags.add(tag_id)

        return instance
