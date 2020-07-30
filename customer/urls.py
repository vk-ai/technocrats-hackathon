from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('video-feed', video_feed, name="video_feed"),
    path('api/sales-rep-register', SalesRepresentativeRegister.as_view()),
    path('api/sales-rep-login', SalesRepresentativeLogin.as_view()),
    path('api/cust_details_purchase_history/<int:user_id>', CustomerProfileAndPurchaseHistoryAPI.as_view()),
    path('api/cust-order-details/<int:user_id>', CustomerPurchaseHistoryAPI.as_view()),
    path('api/sales-rep-details/<int:sales_id>', SalesRepresentativeDetailsAPI.as_view()),
    path('api/logout', SalesRepresentativeLogout.as_view()),
    path('api/list-offers', ListOffersAPI.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)