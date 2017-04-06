from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^$', Checkout.as_view(), { 'template_name':'checkout.html'}, name='checkout'),
    url(r'^get_data',GetData.as_view(),name="get_shipping_address"),
    url(r'^get_shipping_rates',GetShippingRates.as_view(),name="get_shipping_rates"),
    url(r'^make_payment',RunPayments.as_view(),name="make_payment"),
    url(r'^order_history',OrderHistory.as_view(),{ 'template_name':'order_history.html'},name="order_history")
] 

