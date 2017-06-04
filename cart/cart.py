from models import CartItem,CartNote
from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,Http404
from helper import safe_cast,is_user_business,get_prices,get_products_availability
import decimal,uuid
from odoo.models import ProductAttributeValue
from odoo_helpers import OdooAdapter
from django.db.models import Q

from __builtin__ import True

CART_ID_SESSION_KEY = "cart_id"

# get the current user's cart id, sets new one if blank
def _cart_id(request):
    if request.session.get(CART_ID_SESSION_KEY,'') == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]

def get_cart_note(request):
    try:
        return CartNote.objects.get(cart_id=_cart_id(request))
    except CartNote.DoesNotExist:
        return False

def _generate_cart_id():
    return uuid.uuid4().hex

# return all items from the current user's cart
def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(Q(user_id=request.user.id) | Q(cart_id=_cart_id(request)))
    else:
        return CartItem.objects.filter(cart_id=_cart_id(request),user_id__isnull=True)

def add_to_cart(request):
    postdata = request.POST.copy()
    try:
        flavor_id = int(postdata.get('flavor_id',False))
        volume_id = int(postdata.get('volume_id',False))
        conc_id = int(postdata.get('conc_id',False))
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page" 
    except (ValueError,TypeError) as e:
        raise Http404("Sorry! Failed to add product to cart") 
    except AssertionError as e:
         raise Http404(e)
    # get quantity added , return 1 if empty
    quantity = int(postdata.get('quantity',1))
    #fetch the product or return a missing page error
    p = get_object_or_404(ProductVariant,vol_id=volume_id,conc_id=conc_id,flavor_id=flavor_id,active=True,product_tmpl_id__type="product")
    # get products in cart
    cart_products = get_cart_items(request)
    # Check to see if item already in cart
    product_in_cart=False
    available_qty = get_products_availability(p.id)[str(p.id)]
    added = False
    cart_quantity = 0
    for cart_item in cart_products:
        if cart_item.product_id == p.id:
            #upddate the quantity if found
            product_in_cart = True
            cart_quantity = cart_item.quantity+quantity
            if cart_quantity <= available_qty.get('virtual_available',0):
                cart_item.augment_quantity(quantity)
                added=True

    if not product_in_cart:
        cart_quantity = quantity
        if cart_quantity <= available_qty.get('virtual_available',0):
            #create and save a new cart item
            ci = CartItem()
            ci.product_id = p.id
            ci.quantity = quantity
            ci.cart_id = _cart_id(request)
            if request.user.is_authenticated:
                ci.user_id = request.user
            ci.save()
            added = True

    return available_qty,cart_quantity,added



# return the total number of items in user's cart
def cart_distinct_item_count(cart_items=[]):
    return len(cart_items)
    
def get_cart_total(cart_items):
    total = 0.00
    total = round(sum([item.get_total for item in cart_items]),2)
    return total

def get_cart_discount(cart_items,request):
    volume_dictionary_count = {}
    discount = 0.0
    if len(cart_items) > 0:
        if request.user.is_authenticated():
            if is_user_business(request.user):
                return discount
        for item in cart_items:
            if item.product.vol_id.id in volume_dictionary_count:
                volume_dictionary_count[item.product.vol_id.id] = volume_dictionary_count[item.product.vol_id.id] + item.quantity
            else:
                volume_dictionary_count[item.product.vol_id.id] = item.quantity
    for key,val in volume_dictionary_count.iteritems():
        item_count = int(val/4)
        price = get_prices(request.user,ProductAttributeValue.objects.get(id = key))
        discount = discount + (float(price) * item_count)
    return discount

def get_discount_percentage(cart_total,discount):
    discount_percentage = 0.00
    if cart_total > 0:
        discount_percentage = round((discount*100.00/cart_total),2)
    return discount_percentage

def get_net_total(discount_percentage,cart_total):
    net_total = ((100.00 - discount_percentage)/100.00)*cart_total
    return net_total

def create_sale_order_from_cart(request,prtnr=False,**kwargs):
    # Accept partner paramter if the user is not logged in
    vals = {}
    order = False
    order_lines = []
    cart_items = request.CART_DATA.get('actual_cart_items',[])
    cart_items = cart_items.filter(checkedout=True)
    transaction_id = kwargs.get('transaction_id',None)
    if len(cart_items) > 0:
        partner_id = False
        if prtnr:
            partner_id = prtnr.id
        elif request.user.is_authenticated():
            partner_id = request.user.odoo_user.partner_id.id
        note = get_cart_note(request)
        odoo_adapter = OdooAdapter()
        cart_total = get_cart_total(cart_items)
        discount = get_cart_discount(cart_items, request)
        discount_percentage = get_discount_percentage(cart_total,discount)
        for item in cart_items:
            order_lines.append((0,0,{
                    'product_id':item.product_id,
                    'product_uom_qty':item.quantity,
                    'price_unit':item.get_price,
                    'discount':discount_percentage,
                }))
        vals = {
            'partner_id':partner_id or item.partner_id,
            'order_line':order_lines,
            'origin':transaction_id and  "Transaction ID - %s"%(transaction_id) or '',
            'note':note and note.note or '',
            'shipping_cost':note and note.shipping_cost or 0.00,
        }
        order = odoo_adapter.execute_method('sale.order','create_sale_order_from_cart',[vals])
    return order
        