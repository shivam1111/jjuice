from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^$', Cart.as_view(), { 'template_name':'cart.html'}, name='show_cart'),
    url(r'^quick_show_cart/(?P<id>[0-9]+)/$',QuickCart.as_view(),{ 'template_name':'flavor_quick_cart.html'}, name='quick_show_cart'),
    url(r'^add_to_cart/$',AddToCart.as_view(),{ 'template_name':'flavors.html'}, name='add_to_cart'),
] 