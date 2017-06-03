from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import HttpResponse,render
from django.contrib.auth import authenticate
from odoo.models import Partner,ResUsers
from odoo_helpers import OdooAdapter
from helper import login
import base64,requests
from datetime import datetime, timedelta



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



class ForgotPassword(View):
    def post(self,request):
        from django.contrib.auth import get_user_model
        User = get_user_model()        
        status = 200
        params = request.POST.copy()
        data = {
                'error':False,
            }
        if params.get('piNewPass',False) and params.get('token',False):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                name = "Reset Password"
                user = User.objects.get(token_expiration__gte=datetime.now(),token_password=params.get('token',False))
                odoo_adapter = OdooAdapter()
                odoo_adapter.execute_method('res.users', 'update_password', params_list=[user.odoo_user.id,params.get('piNewPass',False)])
                user.token_password = None
                user.save()
            except User.DoesNotExist:
                data.update({
                    'error':True,
                    'msg':"Sorry! The link has expired. Please generate the link again"
                })
            return JsonResponse(data=data, status=status, safe=False)

        if params.get('email',False):
            try:
                odoo_user = ResUsers.objects.get(login=params.get('email',False))
                user = User.objects.get(odoo_id=odoo_user.id)
                user.send_reset_password_mail(request) 
            except ResUsers.DoesNotExist:
                data.update({
                        'error':True,
                        'msg':"Sorry! We do not have this email ID registered with us"
                    })
            except User.DoesNotExist:
                data.update({
                        'error':True,
                        'msg':"Sorry! We do not have this email ID registered with us"
                    })
        else:
            data.update({
                'error':True,
                'msg':"Please enter a valid Email ID."
            })
        return JsonResponse(data=data, status=status, safe=False)

    def get(self,request):
        token = request.GET.get('token',False)
        if token:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                name = "Reset Password"
                user = User.objects.get(token_expiration__gte=datetime.now(),token_password=token)
                return render(request,'change_password.html',locals())
            except User.DoesNotExist:
                exception = "Sorry! The link has expired. Please generate again"
                return render(request, "404.html", locals())
        else:
            exception = "Sorry this link is invalid"
            return render(request,"404.html",locals())
        

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


class OdooSignup(View):

    def post(self,request):
        status = 200
        from django.contrib.auth import get_user_model
        from odoo.models import ResUsers
        User = get_user_model()
        res = {
            'error':True
        }
        # < QueryDict: {u'signup_enabled': [u'True'], u'name': [u'SanDeep'], u'db': [u'jjuice'],
        #               u'token': [u'HuSivPfjNgWwOIA8Ni7m'], u'reset_password_enabled': [u'False'],
        #               u'login': [u'shivam1111@gmail.com']} >
        data = request.POST.copy()
        authorize = authenticate(username = data.get('website_username'),password = data.get('website_password'))
        if authorize:
            # this means the request is authorized to create a new user
            try:
                res_user = ResUsers.objects.get(login=data.get('login', False))
                User.objects.create_user(username=data.get('login', False), email=data.get('login', False), odoo_id=res_user.id)
                res = {
                    'error':False
                }
            except Exception as e:
                pass
        return JsonResponse(data=res, status=status, safe=False)

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
        