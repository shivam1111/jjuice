from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^$', Checkout.as_view(), { 'template_name':'checkout.html'}, name='checkout'),
] 

