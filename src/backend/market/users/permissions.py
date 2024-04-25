from rest_framework.permissions import BasePermission


class IsSupplier(BasePermission):
    """
    Allows access only to Suppliers users.
    """

    def has_permission(self, request, view):
        # user must have profile
        return bool(request.user and request.user.profile.is_supplier)


class IsOwnerUser(BasePermission):
    """
    Object-level permission to allows access to object only to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsNotAdmin(BasePermission):
    """
    Allows access only to not Admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and not request.user.is_staff)


class IsOwnerOrAdminUser(BasePermission):
    """
    Object-level permission to allows access to object only to owners or admins.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return hasattr(obj, 'owner') and obj.owner == request.user or request.user.is_staff
