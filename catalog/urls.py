from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^$', Index.as_view(), { 'template_name':'catalog/index.html'}, name='catalog_home'),
    url(r'^volume/(?P<id>[0-9]+)/$', Volume.as_view(), { 'template_name':'volumes_grid.html'}, name='volume'),
    url(r'^volumes_list/(?P<id>[0-9]+)/$', Volume.as_view(), { 'template_name':'volumes_list.html'}, name='volumes_list'),
    url(r'^flavor/(?P<id>[0-9]+)/$', Flavor.as_view(), { 'template_name':'flavors.html'}, name='flavor'),
    url(r'^flavor_quick_view/(?P<id>[0-9]+)/$', FlavorQuickView.as_view(), { 'template_name':'flavor_quick_view.html'}, name='flavor_quick_view'),
] 

# urlpatterns = patterns('ecomstore.catalog.views',
# , (r'^category/(?P<category_slug>[-\w]+)/$',  
# 'show_category', { 'template_name':'catalog/category.html'},'catalog_category'),
# (r'^product/(?P<product_slug>[-\w]+)/$',   'show_product', {
# 'template_name':'catalog/product.html'},'catalog_product'), )