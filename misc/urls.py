from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^newsletter', newsletter,name='newsletter'),
] 

