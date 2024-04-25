from django.urls import path
from rest_framework.routers import DefaultRouter

from utils.views import HealthView

urlpatterns = [
    path(r'health/', HealthView.as_view(), name='health-check')
]
