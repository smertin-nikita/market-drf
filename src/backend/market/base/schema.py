from django.db.models import Prefetch
from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema


class Fix1(OpenApiViewExtension):
    target_class = 'backend.views.BasketItemViewSet'

    def view_replacement(self):
        from orders.models import Order

        class Fixed(self.target_class):
            queryset = Order.objects.all()

        return Fixed


class Fix2(OpenApiViewExtension):
    target_class = 'dj_rest_auth.registration.views.RegisterView'

    def view_replacement(self):
        from users.serializers import RegisterSerializer

        class Fixed(self.target_class):
            serializer_class = RegisterSerializer

        return Fixed


class Fix3(OpenApiViewExtension):
    target_class = 'dj_rest_auth.views.UserDetailsView'

    def view_replacement(self):
        from users.serializers import UserSerializer

        class Fixed(self.target_class):
            serializer_class = UserSerializer

        return Fixed
