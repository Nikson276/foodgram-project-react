from rest_framework import status
from rest_framework.exceptions import APIException


class ObjectNotFound(APIException):
    """ Class helper with exceptions 400"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Объект не найден'
    default_code = 'Not found'
