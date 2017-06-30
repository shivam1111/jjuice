from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^ratings/$', Ratings.as_view(), { 'template_name':'catalog/index.html'}, name='ratings'),
]