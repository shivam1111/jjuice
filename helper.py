from django.conf import settings
import os,json
from django.http import Http404
from django.http import JsonResponse
from odoo_helpers import OdooAdapter
from django.core.urlresolvers import reverse

def get_item_deails(items):
    res = {}
    if not isinstance(items,list):
        items = [items]
    for item in items:
        res.update({
            item.id: {
                'flavor_url': item.product.get_url(),
                'image_url': item.product.get_image_url(),
                'price': item.get_price,
                'quantity': item.quantity,
                'name': item.product.get_name(),
                'product_id':item.product_id,
                'item_total':item.get_total,
            }})
    return res

def canbe_checkedout(item):
    # deny the rendering if we do not have the right data available
    return item.get('quantity',0) <= item.get('qty',{}).get('virtual_available',1)

def get_cart_data(request,context={}):
    from cart import cart
    # expand : boolean; if true then the cart items will returned in dictionary along with values, else direct browsed objects will be returned
    cart_items = cart.get_cart_items(request)
    item_ids = []
    res = {'cart_items':{}}
    for item in cart_items:
        item_ids.append(item.product.id)
        res['cart_items'].update(get_item_deails(item))
    result_quantities = get_products_availability(item_ids)
    final_items_list = []
    for item in cart_items:
        available_qty = result_quantities.get(str(item.product_id),{'virtual_available':0})
        res['cart_items'][item.id].update({'qty':available_qty})
        if canbe_checkedout(res['cart_items'][item.id]):
            final_items_list.append(item)
    cart_total = cart.get_cart_total(final_items_list)
    discount = cart.get_cart_discount(final_items_list,request)
    discount_percentage = cart.get_discount_percentage(cart_total,discount)
    net_total = round(cart.get_net_total(discount_percentage,cart_total), 2)
    cart_item_count = cart.cart_distinct_item_count(final_items_list)
    res.update({
        'cart_item_count': cart_item_count,
        'discount_percentage': discount_percentage,
        'discount':discount,
        'net_total': net_total,
        'cart_total': cart_total,
        'checkout_cart_items':final_items_list,
        'actual_cart_items':cart_items
    })
    return res


def get_products_availability(ids):
    if isinstance(ids,int):
        ids = [ids]
    odoo_adapter = OdooAdapter()
    result = odoo_adapter.execute_method('product.product', 'get_product_availability',[ids])
    return json.loads(result)

def get_prices(user,volume):
    if user and (not user.is_anonymous()):
        price_line = user.odoo_user.partner_id.volume_price_line_ids.filter(product_attribute_id=volume.id)[:1]
        if price_line.exists():
            return price_line[0].price
        elif user.odoo_user.partner_id.is_company:
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
    response = JsonResponse(data={
            'auth':auth
        },status=200)
    response.set_cookie(CART_ID_SESSION_KEY,cart_id)
    response.delete_cookie('as_custom_verified')
    return response

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
                'email':billing_partner[0].email or odoo_partner.email or '',
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
        elif user.odoo_user.partner_id.is_company:
            return True
        else :
            return False
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