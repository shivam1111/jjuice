from django.conf.urls import url
from views import *
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
        url(r'^upload/$', UploadProfileImage.as_view(),name='upload'),
        url(r'^ajax_login/$', Login.as_view(),name='login'),
        url(r'^captcha/$', CheckReCaptcha.as_view(), name='captcha'),
        url(r'^registration/$', Registration.as_view(), name='registration'),
       url(r'^validate_username/$', ValidateUserName.as_view(), name='validate_username'),
       url(r'^forgot_password/$', csrf_exempt(ForgotPassword.as_view()), name='forgot_password'),
        url(r'^odoo_signup/$', csrf_exempt(OdooSignup.as_view()), name='odoo_signup'),

]
 