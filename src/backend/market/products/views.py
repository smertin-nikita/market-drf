from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, OR
from rest_framework.response import Response

from products.filters import ProductInfoFilter
from products.models import Product, ProductInfo, ProductParameter, Parameter, Category, Shop
from products.permissions import IsNotSupplier
from products.serializers import (
    ProductSerializer,
    ProductInfoSerializer,
    ParameterSerializer,
    CategorySerializer,
    ShopSerializer
)
from users.permissions import IsSupplier, IsNotAdmin, IsOwnerUser


@extend_schema_view(
    list=extend_schema(
        summary="List all the products.",
        description="Return a list of all products.",
    ),
    retrieve=extend_schema(
        summary="Retrieve product.",
        description="Get detail of a specific product.",
    ),
    create=extend_schema(
        summary="Create product.",
        description="Create and return product's details.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update product.",
        description="Update product details by id.",
    ),
    destroy=extend_schema(
        summary="Delete product.",
        description="Delete product by id.",
    ),
    detailed=extend_schema(
        summary="Product information.",
        description="Return advanced information about product.",
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    Viewset for products
    """
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ('category',)

    @action(detail=True, methods=['get'])
    def detailed(self, request, pk):
        instances = ProductInfo.objects.filter(product=pk)
        serializer = ProductInfoSerializer(instances, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        """Define action access."""
        if self.action == "create":
            return [IsAuthenticated(), OR(IsAdminUser(), IsSupplier())]
        elif self.action in ["partial_update", "update", 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return super(ProductViewSet, self).get_permissions()


@extend_schema_view(
    list=extend_schema(
        summary="List all the product's information.",
        description="Return a list of all information about the product.",
    ),
    retrieve=extend_schema(
        summary="Retrieve order.",
        description="Get the detail of specific information about the product.",
    ),
    create=extend_schema(
        summary="Create product's information.",
        description="Create and return details of information about the product.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update product's information.",
        description="Update details of information about the product by id.",
    ),
    destroy=extend_schema(
        summary="Delete product's information..",
        description="Delete product's information by id.",
    )
)
class ProductInfoViewSet(viewsets.ModelViewSet):
    """
    Viewset для информации о продукте.
    """
    product_parameter_set = ProductParameter.objects.select_related('parameter')
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related(
        Prefetch('product_parameters', queryset=product_parameter_set))

    permission_classes = [IsAuthenticated]
    serializer_class = ProductInfoSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'price_rcc', 'quantity']
    search_fields = ['model']

    filterset_class = ProductInfoFilter

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ['create', "partial_update", "update", 'destroy']:
            return [IsAuthenticated(), OR(IsAdminUser(), IsSupplier())]
        else:
            return super(ProductInfoViewSet, self).get_permissions()


@extend_schema_view(
    list=extend_schema(
        summary="List all the parameters.",
        description="Return a list of all parameters.",
    ),
    retrieve=extend_schema(
        summary="Retrieve parameter.",
        description="Get detail of a specific parameter.",
    ),
    create=extend_schema(
        summary="Create parameter.",
        description="Create and return parameter's details.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update parameter.",
        description="Update parameter details by id.",
    ),
    destroy=extend_schema(
        summary="Delete parameter.",
        description="Delete parameter by id.",
    )
)
class ParameterViewSet(viewsets.ModelViewSet):
    """
    Viewset for parameters
    """
    queryset = Parameter.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ParameterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated(), OR(IsAdminUser(), IsSupplier())]
        elif self.action in ["partial_update", "update", 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return super(ParameterViewSet, self).get_permissions()


@extend_schema_view(
    list=extend_schema(
        summary="List all the categories.",
        description="Return a list of all categories.",
    ),
    retrieve=extend_schema(
        summary="Retrieve category.",
        description="Get detail of a specific category.",
    ),
    create=extend_schema(
        summary="Create category.",
        description="Create and return category's details.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update category.",
        description="Update category details by id.",
    ),
    destroy=extend_schema(
        summary="Delete category.",
        description="Delete category by id.",
    )
)
class CategoryViewSet(viewsets.ModelViewSet):
    """Viewset for categories"""
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated(), OR(IsAdminUser(), IsSupplier())]
        elif self.action in ["partial_update", "update", 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        else:
            return super(CategoryViewSet, self).get_permissions()


@extend_schema_view(
    list=extend_schema(
        summary="List all the shops.",
        description="Return a list of all shops.",
    ),
    retrieve=extend_schema(
        summary="Retrieve shop.",
        description="Get the detail of specific shop.",
    ),
    create=extend_schema(
        summary="Create shop.",
        description="Create and return details of shop.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update shop.",
        description="Update details of shop by id.",
    ),
    destroy=extend_schema(
        summary="Delete shop.",
        description="Delete shop by id.",
    ),
    import_data=extend_schema(
        summary="Import data.",
        description="Import shop's data from file.",
    ),
    export_data=extend_schema(
        summary="Export data.",
        description="Return shop's data.",
    )
)
class ShopViewSet(viewsets.ModelViewSet):
    """
    Viewset для магазина.
    """
    queryset = Shop.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ShopSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated(), IsNotSupplier(), IsNotAdmin()]
        elif self.action in ["partial_update", "update"]:
            return [IsAuthenticated(), IsSupplier(), IsOwnerUser(), IsNotAdmin()]
        elif self.action == "destroy":
            return [IsAuthenticated(), OR(IsAdminUser(), IsSupplier())]
        else:
            return super(ShopViewSet, self).get_permissions()
