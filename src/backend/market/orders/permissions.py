from rest_framework.permissions import BasePermission

from orders.models import OrderStatus


class IsOwnerAndIsBasketStatus(BasePermission):
    """
    Позволяет обновлять заказ только собственнику если он в корзине
    """
    message = 'Пользователь может изменять только свою корзину'

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `status`.
        check = obj.status == OrderStatus.BASKET and obj.owner == request.user
        status = request.data.get('status')
        if check and status is not None:
            self.message = 'Вы не можете изменить статус заказа.'
            return False
        return check


class IsAdminAndIsNotBasket(BasePermission):
    """
    Позволяет обновлять заказ только собственнику если он в корзине
    """
    message = 'Админ может изменять только статус заказа и только не на статус корзины'

    def has_object_permission(self, request, view, obj):
        check = request.user.is_staff
        check_status = True
        status = request.data.get('status')
        if status is not None:
            check_status = status != OrderStatus.BASKET

        order_items = request.data.get('order_items')
        if check and order_items is not None:
            self.message = 'Админ не может изменить позиции в заказе.'
            return False

        return check and check_status
