from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^$', Index.as_view(), { 'template_name':'catalog/index.html'}, name='catalog_home'),
    url(r'^volume/(?P<id>[0-9]+)/(?P<view>form|list)/$', Volume.as_view(), { 'template_name':'volumes_grid.html'}, name='volume'),
    url(r'^flavor_review/$', FlavorReview.as_view(), name='flavor_review'),
    url(r'^flavor/(?P<id>[0-9]+)/$', Flavor.as_view(), { 'template_name':'flavors.html'}, name='flavor'),
    url(r'^flavor_quick_view/(?P<id>[0-9]+)/$', FlavorQuickView.as_view(), { 'template_name':'flavor_quick_view.html'}, name='flavor_quick_view'),
    url(r'^search/$', Search.as_view(), { 'template_name':'search.html'}, name='search'),
] 

