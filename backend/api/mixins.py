from rest_framework.exceptions import PermissionDenied, AuthenticationFailed


class PermissionMixin:

    def check_auth_permision(self):
        """ Check if user is authorized or raise exception"""
        if self.request.user.id is None:
            raise AuthenticationFailed({"detail": "Учетные данные не были предоставлены."})

    def check_author_permision(self):
        """ Check if user is author or raise exception"""
        obj = self.get_object()
        if self.request.user != obj.author:
            raise PermissionDenied({"message": "You don't have permission"})