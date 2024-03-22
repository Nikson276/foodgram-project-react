from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """ Новый класс пагинации с лимитом из парметра limit"""

    page_size_query_param = 'limit'
    max_page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
