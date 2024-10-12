from rest_framework import permissions


class IsOwnerOfProject(permissions.BasePermission):
    """
    Custom permission to only allow owners of the project to access it.
    """

    def has_permission(self, request, view):
        # This check happens before accessing the object.
        # It allows the request if the user is authenticated.
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Instance must have a project attribute and the user
        #  must be the owner of the project
        return obj.project.user == request.user
