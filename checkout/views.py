from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from helper import safe_cast
from urllib import quote
import os,requests
from django.conf import settings
from catalog.models import S3Object,SaleOrder
from odoo.models import country_allowed_shipping,country_ids,Country,State,Partner,IrConfigParameters
from helper import create_aws_url,get_user_detail,get_states_list,is_allowed_shipping,is_user_business
from django.http import JsonResponse,HttpResponse,HttpResponseNotFound
from django.core.urlresolvers import reverse
from odoo_helpers import OdooAdapter
from cart.cart import _cart_id,get_cart_items,get_cart_total,create_sale_order_from_cart
from cart.models import CartNote
import xml.etree.ElementTree as ET

class OrderHistory(View):
    def get(self,request,template_name = "order_history.html"):
        orders = []
        if request.user.is_authenticated():
            if request.GET.get('order_id',False):
                order = SaleOrder.objects.get(id=request.GET.get('order_id',0))
                pdf = order.get_invoice()
                response = HttpResponse(content_type='application/pdf;base64')
                response['Content-Disposition'] = 'attachment; filename="%s.pdf"'%(request.GET.get('name',"JJuice Order"))
                out_decode = pdf[0][0].decode('base64')
                response.write(out_decode)
                return response
            partner_id = request.user.odoo_user.partner_id
            order_ids= partner_id.order_ids.filter(state__in=['progress','done']).order_by('-date_order')
            return render(request,template_name,locals())
        else:
            return HttpResponseNotFound(data={})
            
        

class RunPayments(View):
    def post(self,request,format=None):
        if request.user.is_authenticated():
            step = request.POST.get('step',False)
            assert step , "Step value is required"
            headers = {'Content-Type': 'text/xml'}
            next_step = False
            api_key = IrConfigParameters.objects.get_param('nmi_key','No key')
            note,created = CartNote.objects.get_or_create(cart_id=_cart_id(request))
            note.note = request.POST.get('note','')
            note.shipping_cost = request.POST.get('shipping_cost',0.00)
            note.save()
            if step == "step1":
                total = request.POST.get('total',0.00)
                redirect_uri = request.build_absolute_uri(reverse('checkout:make_payment', args=[]))
                xml_string = '''
                            <sale>
                                <api-key>%s</api-key>
                                <redirect-url>%s</redirect-url>
                                <amount>%s</amount>
                            </sale>
                '''%(api_key,redirect_uri,total)
                result = requests.post('https://secure.nmi.com/api/v2/three-step', data=xml_string, headers=headers)
                next_step = 'step2'
            
            return JsonResponse(data={
                    'xml_string':result.text,
                    'next_step':next_step,
                },status=int(result.status_code),safe=True)
    
    def get(self,request):
        token_id  = request.GET.get('token-id',False)
        if (token_id):
            headers = {'Content-Type': 'text/xml'}
            api_key = IrConfigParameters.objects.get_param('nmi_key','No key')
            xml_string = '''
                <complete-action>
                    <api-key>%s</api-key>
                    <token-id>%s</token-id>
                </complete-action>
            '''%(api_key,token_id)
            result = requests.post('https://secure.nmi.com/api/v2/three-step', data=xml_string, headers=headers)
            print result.text
            tree = ET.fromstring(result.text)
            result_code = tree.find('result-code').text
            if result_code == "100":
                # Transaction Was Successfull and now redirect the user to acknowledgement page
                amount = tree.find('amount').text
                transaction_id = tree.find('transaction-id').text
                order = create_sale_order_from_cart(request,transaction_id = transaction_id)
                name = order.get('order_name','Order')
                display_transaction_status = True
                cart_items = get_cart_items(request)
                cart_items.delete()                
                return render(request,'order_acknowledgement.html',locals())
            elif  result_code == "300":
                return redirect('/')
            else:
                # Transaction Was UnSuccessfull and now redirect the user to unsuccessfull page
                order=False
                return render(request,'order_acknowledgement.html',locals())
        return JsonResponse(data={},status=404,safe=True)
        
        

class GetShippingRates(View):
    _name = "Get Shipping Rates"
    
    def get(self,request):
        address = {
            'country_id':int(request.GET.get('country_id',False)),
            'zip':request.GET.get('zip',False),
        }
        response = {
            'error':True,
            'msg':'The Cart is Empty.',
        }
        cart = get_cart_items(request)
        if cart.exists():
            cart_items = map(lambda x:(x.product_id,x.quantity),cart)
            cart_total = get_cart_total(request)
            is_business = is_user_business(request.user)
            if not is_business:
                if cart_total > 55:
                    response['error'] = False
                    response['rate'] = 0.00
                    response['msg'] = "Free Shipping"
                    return JsonResponse(data=response,status=200,safe=True)                   
            odoo_adapter = OdooAdapter()
            resp = odoo_adapter.execute_method('rate.fedex.request','calculate_rates_for_address',params_list=[address,cart_items])
            rate = resp.get('rate',False)
            if rate:
                response['error'] = False
                response['rate'] = rate
                response['msg'] = ""
            else:
                response['msg'] = request_id.response
            return JsonResponse(data=response,status=200,safe=True)
        else:
            return HttpResponseNotFound('Sorry! Cart is Empty')

class GetData(View):
    _name = "Get User Details"
    
    def post(self,request):
        if request.POST.get('adr_key',False) and request.user.is_authenticated():
            odoo_partner = request.user.odoo_user.partner_id
            param = request.POST.copy()
            adr_key = param.get('adr_key',False)
            if adr_key == 'shipping_address':
                shipping_partner = odoo_partner.child_ids.filter(type='delivery')[:1]
                if not shipping_partner.exists():
                    shipping_partner = Partner() 
                else:
                    shipping_partner = shipping_partner[0]                
                shipping_partner.type = "delivery"
                shipping_partner.notify_email = "none"
                shipping_partner.street=param.get('street',False)
                shipping_partner.street2=param.get('street2',False)
                if param.get('name',False):shipping_partner.name=param.get('name',False)
                shipping_partner.state_id=State.objects.get(pk=int(param.get('state_id',False)))
                shipping_partner.city=param.get('city',False)
                shipping_partner.country_id=Country.objects.get(pk=int(param.get('country_id',False)))
                shipping_partner.zip=param.get('zip',False)
                shipping_partner.parent_id = odoo_partner
                shipping_partner.active = True
                shipping_partner.customer = True
                shipping_partner.email = odoo_partner.email
                shipping_partner.save()
            elif adr_key == 'billing_address':
                billing_partner = odoo_partner.child_ids.filter(type='invoice')[:1]
                if not billing_partner.exists():
                    billing_partner = Partner() 
                else:
                    billing_partner = billing_partner[0]                
                billing_partner.type = "invoice"
                billing_partner.notify_email = "none"
                billing_partner.street=param.get('street','')
                billing_partner.street2=param.get('street2','')
                if param.get('name',False):billing_partner.name=param.get('name','No Name')
                billing_partner.state_id=State.objects.get(pk=int(param.get('state_id',0)))
                billing_partner.city=param.get('city','')
                billing_partner.country_id=Country.objects.get(pk=int(param.get('country_id','')))
                billing_partner.zip=param.get('zip','')
                billing_partner.phone=param.get('phone','')
                billing_partner.parent_id = odoo_partner
                billing_partner.active = True
                billing_partner.customer = True
                billing_partner.email = param.get('email','') or odoo_partner.email
                billing_partner.save()                
            return JsonResponse(data={},status=200,safe=True)
        else:
            return HttpResponseNotFound('Please sign in first, to checkout!')
        
        
    def get(self,request):
        name = self._name
        if request.GET.get('states_list',False):
            states_list = Country.objects.get(pk=request.GET.get('states_list',False)).country_state_ids.all()
            states_list =  map(lambda x: (x.id,x.name),states_list)
            return JsonResponse(data={request.GET.get('states_list',False):states_list},status=200,safe=True)
        if request.user.is_authenticated:
            response = {
                'user':False,
                'states_list':{},
                'is_allowed_shipping':True,
                'payment_redirect_url':reverse('checkout:make_payment',args=[]),
                'country_ids':{},
                'state_ids':{}
            }
            for i in country_allowed_shipping:
                response['country_ids'].update({i.id : {'name': i.name,'is_allowed_shipping':True}}) # Name , is shipping allowed
                
            response['subtotal'] = get_cart_total(request)
            partner = request.user.odoo_user.partner_id
            shipping_partner = partner.child_ids.filter(type='delivery')[:1]
            billing_partner = partner.child_ids.filter(type='invoice')[:1]
            if not shipping_partner.exists():
                shipping_partner = partner 
            else:
                shipping_partner = shipping_partner[0]
            if not billing_partner.exists():
                billing_partner = partner 
            else:
                billing_partner = billing_partner[0]                
            user = get_user_detail(request.user)
            response['user']=user
            if shipping_partner and shipping_partner.country_id:
                response['state_ids'][shipping_partner.country_id.id] = {}
                states_list = get_states_list(shipping_partner.country_id)
                for i in states_list:
                    response['state_ids'][shipping_partner.country_id.id].update({i.id:i.name})
                response['country_ids'].update({shipping_partner.country_id.id : {
                                                            'name': shipping_partner.country_id.name,
                                                            'is_allowed_shipping':response['is_allowed_shipping']
                                                        }})                    
                response['is_allowed_shipping'] = is_allowed_shipping(shipping_partner.country_id) #

            if billing_partner and billing_partner.country_id:
                if not (billing_partner.country_id.id == shipping_partner.country_id.id):
                    states_list = get_states_list(billing_partner.country_id)
                    response['state_ids'][billing_partner.country_id.id] = {}
                    for i in states_list: 
                        response['state_ids'][billing_partner.country_id.id].update({i.id:i.name})
                    response['country_ids'].update({billing_partner.country_id.id : {
                                                            'name': billing_partner.country_id.name,
                                                            'is_allowed_shipping':is_allowed_shipping(billing_partner.country_id) #
                                                        }})                                            
            return JsonResponse(data=response,status=200,safe=True)#json_dumps_params are the **kwargs that will be passd to json.dumps
        else:
            return HttpResponseNotFound('Please sign in first, to checkout!')
        
class Checkout(View):
    _name = "Checkout"
    
    def get(self,request,template_name="checkout.html"):
        name = self._name
        if request.user.is_authenticated:
            back_url = request.GET.get('back_url',False)
            back_url_name = request.GET.get('back_url_name','No Name')
            if back_url: 
                back_url = quote(back_url.encode('utf-8'))
            checkout_banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
            banner_record =  S3Object.objects.filter(checkout_banner=True)[:1]
            address = False
            states_list = []
            shipping_allowed = True
            country_allowed_shipping = country_ids.filter(is_shipping_allowed=True)
            if banner_record.exists():
                checkout_banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))
            partner = request.user.odoo_user.partner_id
            address = {
                    'name':partner.name,
                    'is_company':partner.is_company,
                    'street':partner.street,
                    'country_id':partner.country_id and partner.country_id.id or False,
                    'country':partner.country_id and partner.country_id.name,
                    'street2':partner.street2,
                    'city':partner.city,
                    'state':partner.state_id and partner.state_id.name,
                    'state_id':partner.state_id and partner.state_id.id or False,
                    'zip':partner.zip,
                }
            if partner.country_id:
                states_list = partner.country_id.country_state_ids.all()
            if partner.country_id:
                shipping_allowed = partner.country_id in country_allowed_shipping
            countries_list  = map(lambda x:(x.id,x.name),country_allowed_shipping)
            return render(request,template_name,locals())
        else:
            return HttpResponseNotFound('Please sign in first, to checkout!')
        
        
