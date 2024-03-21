import csv

from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response

# coardinates
X_POS = 100
X_END_POS = 300
Y_POS = 800
SM_INDENT_STEP = 10
MD_INDENT_STEP = 20
DEVIDER_INDENT_STEP = 30


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

        p.drawString(X_POS, Y_POS, 'Список рецептов:')
        y = Y_POS - MD_INDENT_STEP
        for recipe in array1:
            p.drawString(X_POS, y, recipe)
            y -= MD_INDENT_STEP
        y -= SM_INDENT_STEP
        p.line(X_POS, y, X_END_POS, y)
        y -= DEVIDER_INDENT_STEP
        p.drawString(X_POS, y, 'Список продуктов:')
        y -= MD_INDENT_STEP
        for pos, amount in array2.items():
            ingredient = f'{pos} --- {amount}'
            p.drawString(X_POS, y, ingredient)
            y -= MD_INDENT_STEP
        p.showPage()
        p.save()

        return response

    def create_file(
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
