from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views import View
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from odoo.models import Partner
from odoo_helpers import OdooAdapter
import base64

class Login(View):

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self,request):
        from cart.cart import _generate_cart_id,CART_ID_SESSION_KEY
        cart_id = ''
        if request.session.get(CART_ID_SESSION_KEY,False):
            cart_id = request.session[CART_ID_SESSION_KEY]
            
        else:
            cart_id = _generate_cart_id()
        form = AuthenticationForm(request, data=request.POST)
        auth = False
        if form.is_valid():
            auth_login(request, form.get_user())
            auth = True
        request.session[CART_ID_SESSION_KEY] = cart_id
        return JsonResponse(data={
                'auth':auth
            },status=200)
        

class UploadProfileImage(View):
    def post(self,request):
        postdata = request.POST.copy()
        image =  request.FILES.get('image',False)
        image_base64 = base64.encodestring(image.read())
        odoo_adapter = OdooAdapter()
        if image:
            odoo_adapter.execute_method('res.partner','write',[request.user.odoo_user.partner_id.id,{'image':image_base64}])
        return HttpResponse(image_base64)
        