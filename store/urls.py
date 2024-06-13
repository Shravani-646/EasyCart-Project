from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from store import views
router = DefaultRouter()
router.register("collections",viewset=views.CollectionViewSet)
router.register("products",viewset=views.ProductViewSet)
router.register("customers",viewset=views.CustomerViewSet,basename="customers")
router.register("carts",viewset=views.CartViewSet)
router.register("orders",viewset=views.OrderViewSet,basename="orders")

cart_router = routers.NestedSimpleRouter(router,"carts",lookup="cart")
cart_router.register("cartitems",viewset=views.CartItemViewSet,basename="cartitems")

order_router = routers.NestedSimpleRouter(router,"orders",lookup="order")
order_router.register("orderitems",viewset=views.OrderItemViewSet,basename="orderitems")

product_router = routers.NestedSimpleRouter(router,"products",lookup="product")
product_router.register("images",viewset=views.ProductImageViewSet,basename="images")

urlpatterns = router.urls + cart_router.urls + order_router.urls + product_router.urls