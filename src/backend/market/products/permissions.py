from rest_framework.permissions import BasePermission


class ShopImportExportPermission(BasePermission):
    """
    Allows access only to Suppliers users to their own shops or to admin users
    """

    message = "Allows access to supplier users to their own shops or to admin users"

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`. user must have profile
        return (
            hasattr(obj, 'owner')
            and obj.owner == request.user
            and request.user.profile.is_supplier
            or request.user.is_staff
        )


class IsNotSupplier(BasePermission):
    """
    Allows access only to not Suppliers users.
    """

    def has_permission(self, request, view):
        # user must have profile
        return bool(request.user and not request.user.profile.is_supplier)
