from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.transaction import atomic
from store.models import Cart, CartItem, Collection, Order, OrderItem,Product,Customer
from decimal import Decimal
from store.signals import order_created

#collection serializer
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id","title","products_count"]

    products_count = serializers.SerializerMethodField(method_name="get_products_count")

    def get_products_count(self,collection):
        return collection.product_set.count()
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = ["id","title","slug","description","unit_price","inventory","collection","price_with_tax"]

    price_with_tax = serializers.SerializerMethodField(method_name="get_price_with_tax")

    def get_price_with_tax(self,product):
        return product.unit_price * Decimal(1*1)
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer 
        fields = ["id","user","phone","birth_date","membership"]

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Cart 
        fields = ["id","created_at","total_price"]

    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self,cart):
        total_price = sum([(i.product.unit_price * i.quantity) for i in cart.cartitem_set.all()])
        return total_price

class CustomProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = ["id","title","unit_price","collection"]

class CartItemSerializer(serializers.ModelSerializer):
    product = CustomProductSerializer()
    class Meta:
        model = CartItem
        fields = ["id","product","quantity","total_price"]

    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self,cartitem):
        return cartitem.product.unit_price * cartitem.quantity


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ["id","product_id","quantity"]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context.get("cart_id")
        product_id = self.validated_data.get("product_id")
        cart_item = CartItem.objects.filter(cart_id=cart_id,product_id=product_id)
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","customer","placed_at","payment_status"]

class AddOrderSerializer(serializers.Serializer):
    id = serializers.UUIDField()

    def validate_id(self,id):
        cart = Cart.objects.filter(id=id)
        if not cart.exists():
            raise ValidationError({"error":"The given cart id does not exists, please check again"})
        if cart.first().cartitem_set.count() == 0:
            raise ValidationError({"error":"A cart can't be empty, try adding products to it."})
        return id


    def save(self, **kwargs):
        with atomic():
            cart_id = self.validated_data["id"]
            user_id = self.context["user_id"]
            cart = Cart.objects.get(id=cart_id)
            customer = Customer.objects.get(user__id=user_id)
            order = Order.objects.create(customer=customer)
            orderitems_list = [OrderItem(order=order,product=item.product,quantity=item.quantity,unit_price=item.product.unit_price) for item in cart.cartitem_set.all()]
            OrderItem.objects.bulk_create(orderitems_list)
            cart.delete()

            order_created.send_robust(sender=self.__class__,order=order)

            return order
    

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
    
class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=8,decimal_places=2,read_only=True)
    class Meta:
        model = OrderItem 
        fields = ["id","order_id","unit_price","product","quantity"]

    def create(self, validated_data):
        order_id = self.context["order_id"]
        product = Product.objects.filter(title=validated_data["product"]).first()
        order = Order.objects.get(id=order_id)
        orderitem = OrderItem.objects.create(order=order,unit_price=product.unit_price,**validated_data)
        return orderitem

class UpdateOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["quantity"]
    

