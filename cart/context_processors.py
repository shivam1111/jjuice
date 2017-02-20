from models import CartItem
import cart


def carts_context(request):
    cart_items = cart.get_cart_items(request)
    cart_item_count = cart.cart_distinct_item_count(request)
    cart_total = cart.get_cart_total(request)
    return {
            'cart_items': cart_items,
            'cart_item_count':cart_item_count,
            'cart_total':cart_total
        }