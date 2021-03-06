from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from urllib import quote
import os,requests,json
from django.conf import settings
from catalog.models import S3Object,SaleOrder
from odoo.models import country_allowed_shipping,country_ids,Country,State,Partner,IrConfigParameters,Partner
from helper import create_aws_url,get_user_detail,get_states_list,is_allowed_shipping,is_user_business,get_cart_data,canbe_checkedout
from django.http import JsonResponse,HttpResponse,HttpResponseNotFound
from django.core.urlresolvers import reverse
from odoo_helpers import OdooAdapter
from cart.cart import _cart_id,get_cart_items,create_sale_order_from_cart
from cart.models import CartNote
import xml.etree.ElementTree as ET
from django.db.models import Q
from datetime import datetime

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
        params = json.loads(request.body)
        step = params.get('step',False)
        assert step , "Step value is required"
        headers = {'Content-Type': 'text/xml'}
        next_step = False
        api_key = IrConfigParameters.objects.get_param('nmi_key','No key')
        note,created = CartNote.objects.get_or_create(cart_id=_cart_id(request))
        note.note = params.get('note','')
        note.shipping_cost = params.get('shipping_cost',0.00)
        note.promotion_code = params.get('promotion_code',"")
        note.save()
        if step == "step1":
            total = params.get('total',0.00)
            redirect_uri = request.build_absolute_uri(reverse('checkout:make_payment'))
            xml_string = '''
                        <sale>
                            <api-key>%s</api-key>
                            <redirect-url>%s</redirect-url>
                            <amount>%s</amount>
                        </sale>
            '''%(api_key,redirect_uri,total)
            result = requests.post('https://secure.nmi.com/api/v2/three-step', data=xml_string, headers=headers)
            next_step = 'step2'
            if not request.user.is_authenticated():
                shipping_address = params.get('shipping_address',False)
                dob = shipping_address.get('dob', "0000-00-00")
                billing_address = params.get('billing_address',False)
                odoo_adapter = OdooAdapter()
                partner = odoo_adapter.create('res.partner',{
                                                            'name':shipping_address.get('name',"No Name"),
                                                            'website_customer':True,
                                                            'classify_finance':'website',
                                                            'acccount_type':'website',
                                                            'type':'contact',
                                                            'email':billing_address.get('email',False),
                                                            'phone':billing_address.get('phone',False),
                                                            'notify_email':'none',
                                                            'birth_date':dob,
                                                            'is_company':False,
                                                                })
                shipping_partner = odoo_adapter.create('res.partner',{
                                            'name':shipping_address.get('name',"No Name"),
                                            'type':'delivery',
                                            'notify_email':'none',
                                            'country_id':shipping_address.get('country_id',0),
                                            'state_id':shipping_address.get('state_id',0),
                                            'street':shipping_address.get('street',False),
                                            'street2': shipping_address.get('street2', False),
                                            'zip': shipping_address.get('zip', False),
                                            'city': shipping_address.get('city', False),
                                            'website_customer':True,
                                            'notify_email': 'none',
                                            'active':True,
                                            'parent_id':partner,
                                            'is_company':False,
                                        })
                billing_partner = odoo_adapter.create('res.partner',{
                                            'name':billing_address.get('name',"No Name"),
                                            'type':'invoice',
                                            'notify_email':'none',
                                            'country_id':billing_address.get('country_id',0),
                                            'state_id':billing_address.get('state_id',0),
                                            'street':billing_address.get('street',False),
                                            'street2': billing_address.get('street2', False),
                                            'zip': billing_address.get('zip', False),
                                            'city': billing_address.get('city', False),
                                            'website_customer':True,
                                            'notify_email': 'none',
                                            'active':True,
                                            'email':billing_address.get('email',False),
                                            'phone':billing_address.get('phone',False),
                                            'parent_id':partner,
                                            'is_company':False,
                                        })
                cart_items = get_cart_items(request)
                for i in cart_items:
                    i.partner_id = partner
                    i.save()
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
            tree = ET.fromstring(result.text)
            result_code = tree.find('result-code').text
            if result_code == "100":
                # Transaction Was Successfull and now redirect the user to acknowledgement page
                amount = tree.find('amount').text
                transaction_id = tree.find('transaction-id').text
                order = create_sale_order_from_cart(request,transaction_id = transaction_id)
                name = order.get('order_name','Order')
                display_transaction_status = True
                cart_items = request.CART_DATA['actual_cart_items'].filter(checkedout=True)
                cart_items.delete()
                request.CART_DATA = get_cart_data(request)
                promotion_id = order.get('promotion_id',False)
                promotion_code = order.get('promotion_code', False)
                response = render(request,'order_acknowledgement.html',locals())
                if not request.user.is_authenticated():
                    # Delete the age verification cookie if it is guest user checkout
                    response.delete_cookie('ac_custom_verified')
                return response
            elif  result_code == "300":
                return redirect(reverse('catalog:catalog_home', args=[])) #if the transaction rerun by refreshing page then take that person out of that page to home page
            else:
                # Transaction Was UnSuccessfull and now redirect the user to unsuccessfull page
                order=False
                display_transaction_status = True
                response = render(request,'order_acknowledgement.html',locals())
                if not request.user.is_authenticated():
                    # Delete the age verification cookie if it is guest user checkout
                    response.delete_cookie('ac_custom_verified')
                return response
        return HttpResponseNotFound()
        
        

class GetShippingRates(View):
    _name = "Get Shipping Rates"
    
    def get(self,request):
        country_id = int(request.GET.get('country_id',False))
        state_id = int(request.GET.get('state_id',False))
        country = Country.objects.get(pk=country_id)
        address = {
            'country_id':country_id,
            'zip':request.GET.get('zip',False),
        }
        response = {
            'error':True,
            'msg':'The Cart is Empty.',
        }
        dob = request.GET.get('dob', "0000-00-00")
        dob_parse = datetime.strptime(dob, "%Y-%m-%d")
        if not request.COOKIES.get('ac_custom_verified'):
            country = Country.objects.get(pk=country_id)
            state = State.objects.get(pk=state_id)
            data_verify = {
                "key": request.agechecker.get('key',""),
                "data": {
                    "address": request.GET.get('street','No Address'),
                    "city": request.GET.get('city','No City'),
                    "country": country.code,
                    "dob_day": dob_parse.day,
                    "dob_month": dob_parse.month,
                    "dob_year": dob_parse.year,
                    "first_name": request.GET.get('name','No Name'),
                    "last_name": "",
                    "state": state.code, # Accepts only two characters
                    "zip": request.GET.get('zip','No zip')
                }
            }
            headers = {'Content-Type': 'application/json'}
            res = requests.post('https://api.agechecker.net/v1/create', data=json.dumps(data_verify), headers=headers)
            res = res.json()
            response.update({
                'agechecker':{
                    'data':data_verify,
                    'response':res,
                }
            })
        else:
            response.update({
                'agechecker':{
                    'response':{'status':'accepted'},
                }
            })
        # {"uuid": "MnZFkxUiOjgC1tZVkzn7XcfX6Tmhs2S6", "status": "photo_id"}
        # {u'error': {u'message': u'Invalid data length.', u'code': u'invalid_data_length'}}
        # {u'error': {u'message': u'DOB is below the minimum age of 18', u'code': u'user_underage'}}
        # {u'status': u'accepted', u'uuid': u'lT2jwXSlIDvGSyc4bbGK38W0TbshkN2C'}
        cart = get_cart_items(request)
        if cart.exists():
            cart_items = map(lambda x: (x.product_id, x.quantity), cart)
            cart_total = float(request.GET.get('cart_total',0))
            is_business = is_user_business(request.user)
            if request.user.is_authenticated():
                Partner.objects.filter(id=request.user.odoo_user.partner_id.id).update(birth_date=dob_parse)
            if is_business:
                type = None
                if request.user.is_authenticated():
                    type = request.user.odoo_user.partner_id.classify_finance
                if (cart_total > 500) and (type not in ["wholesale", 'private_label']):
                    response['error'] = False
                    response['rate'] = 0.00
                    response['msg'] = "Free Shipping"
                    return JsonResponse(data=response, status=200, safe=True)
                else:
                    try:
                        odoo_adapter = OdooAdapter()
                        resp = odoo_adapter.execute_method('rate.fedex.request', 'calculate_rates_for_address',
                                                           params_list=[address, cart_items])
                        rate = resp.get('rate', False)
                        if rate:
                            response['error'] = False
                            response['rate'] = rate
                            response['msg'] = ""
                        else:
                            response['msg'] = resp.get('msg',
                                                       "We were unable to get the shipment rates. Please contact JJuice directly!")
                    except Exception:
                        response['msg'] = "We were unable to get the shipment rates. Please contact JJuice directly!"
                    return JsonResponse(data=response, status=200, safe=True)
            else:
                if cart_total > 55:
                    response['error'] = False
                    response['rate'] = 0.00
                    response['msg'] = "Free Shipping"
                    return JsonResponse(data=response, status=200, safe=True)
                else:
                    response['error'] = False
                    response['rate'] = 2.95
                    response['msg'] = ""
                    return JsonResponse(data=response, status=200, safe=True)
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
            if not request.GET.get('banned',True) or request.GET.get('banned',True) == "false":
                states_list = Country.objects.get(pk=request.GET.get('states_list',False)).country_state_ids.filter(Q(is_banned__isnull=True) | Q(is_banned = False))
            else:
                states_list = Country.objects.get(pk=request.GET.get('states_list', False)).country_state_ids.all()
            states_list =  dict(map(lambda x: (x.id,x.name),states_list))
            return JsonResponse(data={request.GET.get('states_list',False):states_list},status=200,safe=True)
        response = {
            'user': False,
            'states_list': {},
            'is_allowed_shipping': True,
            'payment_redirect_url': reverse('checkout:make_payment', args=[]),
            'country_ids': {},
            'state_ids': {},
            'item_ids':[],
            'age_checked':request.COOKIES.get('ac_custom_verified',False),
            'dob':False,
        }
        for i in country_allowed_shipping:
            response['country_ids'].update(
                {i.id: {'name': i.name, 'is_allowed_shipping': True}})  # Name , is shipping allowed
        cart_data = get_cart_data(request)
        response['subtotal'] = cart_data.get('cart_total',0.00)
        response['gross_total'] = cart_data.get('net_total',0.00)
        for i in request.CART_DATA.get('actual_cart_items',[]):
            if i.checkedout:
                response['item_ids'].append(i.id)
        if request.user.is_authenticated:
            partner = request.user.odoo_user.partner_id
            shipping_partner = partner.child_ids.filter(type='delivery')[:1]
            billing_partner = partner.child_ids.filter(type='invoice')[:1]
            response.update({
              'dob':partner.birth_date,
            })
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
            response.update({'signin_login':reverse('odoo_auth:login',args=[])})
            return JsonResponse(data=response,status=200,safe=True)
        
class Checkout(View):
    _name = "Checkout"
    
    def get(self,request,template_name="checkout.html"):
        name = self._name
        back_url = request.GET.get('back_url', False)
        back_url_name = request.GET.get('back_url_name', 'No Name')
        if back_url:
            back_url = quote(back_url.encode('utf-8'))
        checkout_banner_url = os.path.join(settings.STATIC_URL, settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record = S3Object.objects.filter(checkout_banner=True)[:1]
        if banner_record.exists():
            checkout_banner_url = create_aws_url(banner_record[0]._meta.db_table, str(banner_record[0].id))
        country_allowed_shipping = country_ids.filter(is_shipping_allowed=True)
        countries_list = map(lambda x: (x.id, x.name), country_allowed_shipping)
        address = False
        shipping_allowed = True
        age_checked = request.COOKIES.get('ac_custom_verified',False)
        if request.user.is_authenticated:
            states_list = []
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
        # Running a loop through all cart items to tick which ones are checkedout
        request.CART_DATA['actual_cart_items'].checkedout = False
        for i in request.CART_DATA.get('checkout_cart_items',[]):
            i.checkedout = True
            i.save()
        return render(request,template_name,locals())

