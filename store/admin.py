from django.contrib import admin
from .models import Product, ProductImage
from django.contrib import admin
from .models import Product, Order, OrderItem 

admin.site.register(Order)
admin.site.register(OrderItem)

class ProductImageInline(admin.TabularInline):  
    model = ProductImage
    extra = 1  

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]  #
    list_display = ('name', 'price', 'description')  

admin.site.register(Product, ProductAdmin)

