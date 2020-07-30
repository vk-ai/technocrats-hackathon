from django.contrib import admin
from .models import CustomerProfile, KnownEncoding, SalesRepresentative, Products, Orders, OrderItems, FCMDevice, Offers

# Register your models here.
admin.site.register(CustomerProfile)
admin.site.register(KnownEncoding)
admin.site.register(SalesRepresentative)
admin.site.register(Products)
admin.site.register(Orders)
admin.site.register(OrderItems)
admin.site.register(FCMDevice)
admin.site.register(Offers)