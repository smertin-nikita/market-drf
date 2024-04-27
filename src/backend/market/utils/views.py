from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('GET', 'OPTIONS', 'HEAD')

    def get(self, *args, **kwargs):
        return Response({'status': _('ok')}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')
