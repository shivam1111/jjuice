from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^$', Index.as_view(), { 'template_name':'catalog/index.html'}, name='catalog_home'),
    url(r'^volume/(?P<id>[0-9]+)/$', Volume.as_view(), { 'template_name':'volumes.html'}, name='volume'),
    url(r'^flavor/(?P<id>[0-9]+)/$', Flavor.as_view(), { 'template_name':'flavors.html'}, name='flavor'),
] 

# urlpatterns = patterns('ecomstore.catalog.views',
# , (r'^category/(?P<category_slug>[-\w]+)/$',  
# 'show_category', { 'template_name':'catalog/category.html'},'catalog_category'),
# (r'^product/(?P<product_slug>[-\w]+)/$',   'show_product', {
# 'template_name':'catalog/product.html'},'catalog_product'), )