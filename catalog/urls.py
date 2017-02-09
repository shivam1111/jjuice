from django.conf.urls import url
import views as catalog


urlpatterns = [
    url(r'^$', catalog.index, { 'template_name':'catalog/index.html'}, 'catalog_home'),
] 

# urlpatterns = patterns('ecomstore.catalog.views',
# , (r'^category/(?P<category_slug>[-\w]+)/$',  
# 'show_category', { 'template_name':'catalog/category.html'},'catalog_category'),
# (r'^product/(?P<product_slug>[-\w]+)/$',   'show_product', {
# 'template_name':'catalog/product.html'},'catalog_product'), )