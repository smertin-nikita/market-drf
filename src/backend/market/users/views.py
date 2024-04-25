from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from users.serializers import UserSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all the users.",
        description="Return a list of all users in the system.",
    ),
    retrieve=extend_schema(
        summary="Retrieve user",
        description="Get details of a specific user",
    ),
)
class UserViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
