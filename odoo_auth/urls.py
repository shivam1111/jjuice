from django.conf.urls import url
from views import UploadProfileImage,Login
urlpatterns = [
        url(r'^upload/$', UploadProfileImage.as_view(),name='upload'),
        url(r'^ajax_login/$', Login.as_view(),name='login'),
#         url(r'^register/$', 'register',name='register'),
#         url(r'^my_account/$', 'my_account',{'template_name': 'registration/my_account.html'}, 'my_account'),
#         url(r'^order_details/(?P<order_id>[-\w]+)/$', 'order_details', {'template_name': 'registration/order_details.html'}, 'order_details'),
#         url(r'^order_info//$', 'order_info',{'template_name': 'registration/order_info.html'}, 'order_info'),

]
 