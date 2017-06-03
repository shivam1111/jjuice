from models import CartItem
from helper import get_cart_data

def carts_context(request):
    return get_cart_data(request)