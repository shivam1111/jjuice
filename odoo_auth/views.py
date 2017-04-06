from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from odoo.models import Partner,ResUsers
from odoo_helpers import OdooAdapter
from helper import login
import base64,requests
from odoo_helpers import OdooAdapter



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class ForgotPassword(View):
    def post(self,request):
        status = 200
        return JsonResponse(data={},status=status,safe=False)
        

class ValidateUserName(View):
    
    def get(self,request):
        login = request.GET.get('email',False)
        exists = "true"
        if login:
            # if exists then it value should be False so that i raises error in the front end
            exists = "true" if (not ResUsers.objects.filter(login=login).exists()) else "false"
        return HttpResponse(exists)
        

class Registration(View):
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)    
    def post(self,request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        status = 200
        vals = request.POST.dict()
        data = {
                'error':True
            }
        login = vals.get('email',False)
        if ResUsers.objects.filter(login=login).exists() or User.objects.filter(username=login).exists():
            data.update({
                    'msg':"Sorry this email is already registered with us. Please click on forgot password to reset password"
                })
            return JsonResponse(data=data,status=status,safe=False)            
        odoo_adapter = OdooAdapter()
        try:
            res = odoo_adapter.execute_method('res.users','create_users',params_list=[vals])
            if not res:
                data.update({
                    'msg':"Sorry! Due to some reason registration could not be completed. Please contact JJuice for further assistance. We apologize for inconvenience caused!"
                })
                return JsonResponse(data=data,status=status,safe=False)                
            else:
                User.objects.create_user(username=vals.get('email',False),email=vals.get('email',False),odoo_id=res)
        except Exception as e:
                data.update({
                    'msg':"Sorry! Due to some reason registration could not be completed. Please contact JJuice for further assistance."
                })
                return JsonResponse(data=data,status=status,safe=False)                

        data.update({
                'error':False,
                'is_wholesale':vals.get('is_wholesale',False),
                'login_params':{
                    'username':vals.get('email',False),
                    'password':vals.get('register-confirm-password',False),
                    'next':''                
                }
            })            
        return JsonResponse(data=data,status=status,safe=False)
        

class CheckReCaptcha(View):
    
    def post(self,request,format=None):
        code = request.POST.get('g-recaptcha-response',False)
        status = 404
        data = {
            'success':False
        }
        if code:
            payload = {'response': code,'secret':settings.CAPTCHA_SECRET_KEY,'remoteip':get_client_ip(request)}
            r = requests.post(settings.CAPTCHA_URL, data=payload)
            status = r.status_code
            data = r.json()
        return JsonResponse(data=data,status=status,safe=False)


class Login(View):

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self,request):
#        request.POST -:
#         <QueryDict: {u'username': [u'hello@vapejjuice.com'], 
#         u'csrfmiddlewaretoken': [u'SM696oXH1A9cep0zp21RZgaomQa2eP6cJyf8fQZAnMc81JIpVVZW4Wjq7YyI9VT7'], 
#         u'password': [u'shivam'], u'next': [u'']}>
        return login(request)        

class UploadProfileImage(View):
    def post(self,request):
        postdata = request.POST.copy()
        image =  request.FILES.get('image',False)
        image_base64 = base64.encodestring(image.read())
        odoo_adapter = OdooAdapter()
        if image:
            odoo_adapter.execute_method('res.partner','write',[request.user.odoo_user.partner_id.id,{'image':image_base64}])
        return HttpResponse(image_base64)
        