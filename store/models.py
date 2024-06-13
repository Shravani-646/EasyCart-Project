from django.db import models
from uuid import uuid4
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import admin
# Create your models here.
#Product
class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(to="Product",null=True,related_name="+",on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering = ["title"]

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True,blank=True)
    unit_price = models.DecimalField(max_digits=8,decimal_places=2)
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(to=Collection,on_delete=models.PROTECT)
    promotions = models.ManyToManyField(to=Promotion,blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["title"]
class Customer(models.Model):
    GOLD_MEMBERSHIP = 'G'
    SILVER_MEMBERSHIP = 'S'
    BRONZE_MEMBERSHIP = 'B'
    MEMBERSHIP_CHOICES = [
        (GOLD_MEMBERSHIP,"Gold"),
        (SILVER_MEMBERSHIP,"SILVER"),
        (BRONZE_MEMBERSHIP,"Bronze")
    ]
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1,choices=MEMBERSHIP_CHOICES,default=BRONZE_MEMBERSHIP)


    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']

class Order(models.Model):
    PAYMENT_PENDING = 'P'
    PAYMENT_FAILED = 'F'
    PAYMENT_COMPLETE = 'C'

    PAYMENT_STATUS_OPTIONS = [
        (PAYMENT_PENDING,"Pending"),
        (PAYMENT_FAILED,"Failed"),
        (PAYMENT_COMPLETE,"Complete")
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    payment_status = models.CharField(max_length=1,choices=PAYMENT_STATUS_OPTIONS,default=PAYMENT_PENDING)

class OrderItem(models.Model):
    order = models.ForeignKey(to=Order,on_delete=models.PROTECT)
    product = models.ForeignKey(to=Product,on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8,decimal_places=2)

class Cart(models.Model):
    id = models.UUIDField(default=uuid4,primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(to=Cart,on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'product')

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    #customer = models.OneToOneField(to=Customer,on_delete=models.CASCADE,primary_key=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    zipcode = models.CharField(max_length=30)



