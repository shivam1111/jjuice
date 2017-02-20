from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^$', Cart.as_view(), { 'template_name':'cart/cart.html'}, name='show_cart'),
] 