from rest_framework.throttling import UserRateThrottle


class ShopImportRateThrottle(UserRateThrottle):
    scope = 'shop_import'


class ShopExportRateThrottle(UserRateThrottle):
    scope = 'shop_export'
