from django.conf import settings
import os
from django.http import Http404
from django.http import JsonResponse

def get_prices(user,volume):
    if user and (not user.is_anonymous()):
        price_line = user.odoo_user.partner_id.volume_price_line_ids.filter(product_attribute_id=volume.id)[:1]
        if price_line.exists():
            return price_line[0].price
        elif user.odoo_user.partner_id.classify_finance in ['wholesale', 'private_label']:
            return volume.wholesale_price
    return volume.msrp

def login(request):
    from cart.cart import _generate_cart_id,CART_ID_SESSION_KEY
    from django.contrib.auth.forms import (
        AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
    )    
    from django.contrib.auth import login as auth_login
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

def get_states_list(country):
    from odoo.models import Country
    if not isinstance(country,Country):
        country = Country.objects.get(pk=int(country))    
    return country.country_state_ids.all()

def is_allowed_shipping(country):
    from odoo.models import Country,country_allowed_shipping
    if not isinstance(country,Country):
        country = Country.objects.get(pk=int(country))
    shipping_allowed = country in country_allowed_shipping
    return shipping_allowed


def get_user_detail(user):
    odoo_partner = user.odoo_user.partner_id
    billing_partner = odoo_partner.child_ids.filter(type='invoice')[:1]
    if billing_partner.exists():
        billing_address = {
                'name':billing_partner[0].name or '',
                'phone':billing_partner[0].phone or '',
                'street':billing_partner[0].street or '',
                'street2':billing_partner[0].street2 or '',
                'city':billing_partner[0].city or '',
                'state_id':billing_partner[0].state_id and billing_partner[0].state_id.id or '',
                'country_id':billing_partner[0].country_id and billing_partner[0].country_id.id or '',
                'email':billing_partner[0].email or '',
                'zip':billing_partner[0].zip or '',
            }
    else:
        billing_address={
                'name':'',
                'phone':'',
                'street':'',
                'street2':'',
                'city':'',
                'state_id':False,
                'country_id':False,
                'email':'',
                'zip':'',        
        }
    shipping_partner = odoo_partner.child_ids.filter(type='delivery')[:1]
    if not shipping_partner.exists():
        shipping_partner = odoo_partner
    else:
        shipping_partner = shipping_partner[0]
    details = {
        'name':odoo_partner.name,
        'email':odoo_partner.email,
        'is_company':odoo_partner.is_company,
        'shipping_address':{
                'name':shipping_partner.name or '',
                'street':shipping_partner.street or '',
                'street2':shipping_partner.street2 or '',
                'city':shipping_partner.city or '',
                'state_id':shipping_partner.state_id and shipping_partner.state_id.id or False,
                'country_id':shipping_partner.country_id and shipping_partner.country_id.id or False,
                'zip':shipping_partner.zip or '',
            },
        'billing_address':billing_address,
    }
    return details

def get_product_variants(flavor,volume_id,type='product',sellable=True,purchasable=False):
    return flavor.flavor_product_variant_ids.filter(
                                                active=True,
                                                vol_id = volume_id,
                                                product_tmpl_id__type = 'product',
                                                product_tmpl_id__sale_ok=sellable,
                                                tab_id__vol_id=volume_id,
                                                tab_id__visible_all_customers=True,
                                                tab_id__consumable_stockable = 'product',
                                                tab_id__active = True).distinct('conc_id__id')

def is_user_business(user):
    try:
        if (not user.is_authenticated):
            return False
        elif (not user.odoo_user.partner_id.classify_finance) or (user.odoo_user.partner_id.classify_finance == 'website'):
            return False
        else :
            return True
    except Exception as e:
        return False

def get_price(authenticated,volume,user=None,flavor=None):
    # volume,user,flavor are not ids but instances of the model
    if authenticated:
        pass
    else:
        return volume.msrp

def create_aws_url(key,fname):
    return os.path.join(settings.AWS_BASE_URL,settings.BUCKET,key,fname)

def safe_cast(func):
    def wrapper(self,request,id,template_name):
        try:
            return func(self,request,id,template_name)
        except (ValueError,TypeError) as e:
            raise Http404("Sorry the URL could not be found!")
        except AssertionError as e:
            raise Http404(e)
    return wrapper