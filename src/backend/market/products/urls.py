from rest_framework.routers import DefaultRouter

from products.views import ProductViewSet, ProductInfoViewSet, ParameterViewSet, CategoryViewSet, ShopViewSet

router = DefaultRouter()

router.register(r'products', ProductViewSet, basename='products')
router.register(r'products-info', ProductInfoViewSet, basename='products-info')
router.register(r'parameters', ParameterViewSet, basename='parameters')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'shops', ShopViewSet, basename='shops')


urlpatterns = router.urls
