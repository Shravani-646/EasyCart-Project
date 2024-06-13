from django.shortcuts import render,get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import RetrieveModelMixin,DestroyModelMixin,CreateModelMixin
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter
from store.models import Cart, CartItem, Collection, Customer, Order, OrderItem,Product
from store.serializers import AddCartItemSerializer, AddOrderSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, OrderItemSerializer, OrderSerializer,ProductSerializer,CustomerSerializer, UpdateCartItemSerializer, UpdateOrderItemSerializer, UpdateOrderSerializer
from store.pagination import CustomPagePagination
from store.permissions import IsAdminOrReadOnly
from store.filters import ProductFilter


# Create your views here.
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all().order_by("id")
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {"request":self.request}
    
    def destroy(self, request, *args, **kwargs):
        products_count = self.get_object().product_set.count()
        if products_count > 0:
            raise ValidationError({"error":"Can't delete the collection as it has products associated with it."})
        return super().destroy(request, *args, **kwargs)
    

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    pagination_class = CustomPagePagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().order_by("id")
    serializer_class = CustomerSerializer
    http_method_names = ["get","post","patch","options","put"]
    permission_classes = [IsAdminUser]

    @action(detail=False,methods=["get","options","patch"],permission_classes=[IsAuthenticated])
    def me(self,request):
        customer = Customer.objects.get(user=self.request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(instance=customer)
            return Response(data=serializer.data)
        
        elif request.method == "PATCH":
            serializer = CustomerSerializer(instance=customer,data=request.data,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)


class CartViewSet(RetrieveModelMixin,
                  CreateModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def destroy(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart,id=self.kwargs["pk"])
        if cart.cartitem_set.count() > 0:
            raise ValidationError({'error':"Can't delete the cart as it has items in it."})
        return super().destroy(request, *args, **kwargs)


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get","options","post","patch","delete"]
    def get_serializer_context(self):
        return {'cart_id':self.kwargs["cart_pk"]}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"])
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        if self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer
    
class OrderViewSet(ModelViewSet):

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all().order_by("id")
        customer = get_object_or_404(Customer,user__id=self.request.user.id)
        return Order.objects.filter(customer=customer)
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddOrderSerializer 
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE','PUT']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_context(self):
        return {"user_id":self.request.user.id}
    
    def create(self, request, *args, **kwargs):
        serializer = AddOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(instance=order)
        return Response(data=serializer.data,status=status.HTTP_201_CREATED)
    

class OrderItemViewSet(ModelViewSet):
    http_method_names = ["get","post","options","patch","delete"]

    def get_permissions(self):
        if self.request.method in ["PATCH","DELETE","POST"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return OrderItem.objects.filter(order__id=self.kwargs["order_pk"])
    
    def get_serializer_context(self):
        return {'order_id':self.kwargs["order_pk"]}
    
    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UpdateOrderItemSerializer
        return OrderItemSerializer
        