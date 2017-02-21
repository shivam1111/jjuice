from models import CartItem
from catalog.models import ProductVariant
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,Http404
from helper import safe_cast
import decimal,uuid
from __builtin__ import True

CART_ID_SESSION_KEY = "cart_id"

# get the current user's cart id, sets new one if blank
def _cart_id(request):
    if request.session.get(CART_ID_SESSION_KEY,'') == '':
        request.session[CART_ID_SESSION_KEY] = _generate_cart_id()
    return request.session[CART_ID_SESSION_KEY]


def _generate_cart_id():
    return uuid.uuid4().hex

# return all items from the current user's cart
def get_cart_items(request):
    if request.user.is_authenticated():
        return CartItem.objects.filter(cart_id=_cart_id(request),user_id=request.user)
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
        ci.user_id = request.user.id
        ci.save()        

# return the total number of items in user's cart
def cart_distinct_item_count(request):
    return get_cart_items(request).count()
    
def get_cart_total(request):
    total = 0.00
    cart_items = get_cart_items(request)
    try:
        total = round(sum(item.get_total for item in cart_items),2)
    except Exception as e:
        pass
    return total
        
    

