from django.conf.urls import url
from views import *
from django.contrib.sitemaps.views import sitemap

urlpatterns = [
    url(r'^newsletter', newsletter,name='newsletter'),
    url(r'^aboutus',AboutUs.as_view(),{'template_name':'aboutus.html'},name="aboutus"),
    url(r'^contactus',ContactUs.as_view(),{'template_name':'contactus.html'},name="contactus"),
    url(r'^privacy_policy',PrivacyPolicy.as_view(),{'template_name':'privacy_policy.html'},name="privacy_policy"),
    url(r'^terms_conditions',TermsConditions.as_view(),{'template_name':'terms_conditions.html'},name="terms_conditions"),
] 

