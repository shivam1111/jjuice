from models import CartItem,CartNote
from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,Http404
from helper import safe_cast
import decimal,uuid
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
    for cart_item in cart_products:
        if cart_item.product_id == p.id:
            #upddate the quantity if found
            cart_item.augment_quantity(quantity)
            product_in_cart = True
    if not product_in_cart:
        #create and save a new cart item
        ci = CartItem()
        ci.product_id = p.id
        ci.quantity = quantity
        ci.cart_id = _cart_id(request)
        if request.user.is_authenticated:
            ci.user_id = request.user
        ci.save()        

# return the total number of items in user's cart
def cart_distinct_item_count(request):
    return get_cart_items(request).count()
    
def get_cart_total(request):
    total = 0.00
    cart_items = get_cart_items(request)
    if cart_items.exists():
        try:
            total = round(sum(item.get_total for item in cart_items),2)
        except Exception as e:
            pass
    return total
        
def create_sale_order_from_cart(request,partner=False,**kwargs):
    # Accept partner paramter if the user is not logged in
    vals = {}
    order = False
    if request.user.is_authenticated():
        order_lines = []
        cart_items = get_cart_items(request)
        transaction_id = kwargs.get('transaction_id',None)
        if cart_items.exists():
            partner = partner or request.user.odoo_user.partner_id
            note = get_cart_note(request)
            odoo_adapter = OdooAdapter()
            for item in cart_items:
                order_lines.append((0,0,{
                        'product_id':item.product_id,
                        'product_uom_qty':item.quantity,
                        'price_unit':item.get_price,
                    }))
                vals = {
                    'partner_id':partner.id,
                    'order_line':order_lines,
                    'origin':transaction_id and  "Transaction ID - %s"%(transaction_id) or '',
                    'note':note and note.note or '',
                    'shipping_cost':note and note.shipping_cost or 0.00,
                }
            order = odoo_adapter.execute_method('sale.order','create_sale_order_from_cart',[vals])
    return order
        