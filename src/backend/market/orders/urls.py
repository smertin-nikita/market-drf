from rest_framework.routers import DefaultRouter

from orders.views import OrderViewSet, BasketItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'basket', BasketItemViewSet, basename='basket')


urlpatterns = router.urls
