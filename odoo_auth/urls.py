from django.conf.urls import url
from views import *
urlpatterns = [
        url(r'^upload/$', UploadProfileImage.as_view(),name='upload'),
        url(r'^ajax_login/$', Login.as_view(),name='login'),
        url(r'^captcha/$', CheckReCaptcha.as_view(), name='captcha'),
        url(r'^registration/$', Registration.as_view(), name='registration'),
       url(r'^validate_username/$', ValidateUserName.as_view(), name='validate_username'),
       url(r'^forgot_password/$', ForgotPassword.as_view(), name='forgot_password'),        
]
 