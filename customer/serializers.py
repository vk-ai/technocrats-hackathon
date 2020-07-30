from rest_framework import serializers
from .models import CustomerProfile, SalesRepresentative, Orders, OrderItems, Products, Offers


class ProductDetails(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField('fetch_product_image_path')

    def fetch_product_image_path(self, instance):
        return instance.product_image.url

    class Meta:
        model = Products
        fields = ('name', 'description', 'category', 'product_type', 'prize', 'product_image')


class OrderItemsDetails(serializers.ModelSerializer):
    product_id = ProductDetails()

    class Meta:
        model = OrderItems
        fields = ('order_id', 'product_id', 'quantity')


class OrderHistory(serializers.ModelSerializer):
    id = OrderItemsDetails()

    class Meta:
        model = Orders
        fields = ('id',)



class CustomerProfileAndPurchaseHistorySerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField('fetch_profile_image_path')
    previous_sales_rep = serializers.SerializerMethodField('fetch_previous_sales_rep_name')

    def fetch_profile_image_path(self, instance):
        return instance.profile_image.url

    def fetch_previous_sales_rep_name(self, instance):
        return instance.previous_sales_rep.first_name +" "+ instance.previous_sales_rep.middle_name +" "+ instance.previous_sales_rep.last_name


    class Meta:
        model = CustomerProfile
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'profile_image', 'date_of_birth',
                  'customer_type', 'previous_sales_rep', 'profession')


class SalesRepresentativesDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRepresentative
        fields = ('first_name', 'middle_name', 'last_name', 'email', 'status', 'store')


class OfferDetailsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('fetch_image_path')

    def fetch_image_path(self, instance):
        return instance.image.url

    class Meta:
        model = Offers
        fields = ('category', 'description', 'image')