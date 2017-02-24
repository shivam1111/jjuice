from django.conf.urls import url
from views import *


urlpatterns = [
    url(r'^newsletter', newsletter,name='newsletter'),
    url(r'^aboutus',AboutUs.as_view(),{'template_name':'aboutus.html'},name="aboutus"),
    url(r'^contactus',ContactUs.as_view(),{'template_name':'contactus.html'},name="contactus")
] 

