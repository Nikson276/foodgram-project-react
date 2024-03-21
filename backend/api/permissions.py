from rest_framework import permissions


class AuthorUserOrAdmin(permissions.IsAuthenticated):
    """ Class for custom permission """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.author_id == user.id
