from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from store import models
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models.aggregates import Count
# Register your models here.
#customize the all models in admin site
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ["featured_product"]
    list_display = ["title","products_count"]
    list_per_page = 10
    search_fields = ["title"]

    def products_count(self,collection):
        return collection.product_set.count()
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    list_display = ["title","unit_price","inventory_status","collection_title"]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = ["collection"]
    list_filter = ["collection","last_update"]
    search_fields = ["title"]

    @admin.display(ordering="inventory")
    def inventory_status(self,product):
        return "Low" if product.inventory<10 else "Adequate"
    
    @admin.display(ordering="collection")
    def collection_title(self,product):
        return product.collection.title
    
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id","placed_at","customer_name"]
    ordering = ["id"]
    inlines = [OrderItemInline]
    list_filter = ["placed_at"]
    
    @admin.display(ordering="customer")
    def customer_name(self,order):
        return order.customer.user.first_name

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',  'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(orders_count=Count("order"))
