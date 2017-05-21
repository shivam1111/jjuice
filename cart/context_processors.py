from models import CartItem
import cart

def carts_context(request):
    cart_items = cart.get_cart_items(request)
    cart_item_count = cart.cart_distinct_item_count(request)
    cart_total = cart.get_cart_total(request)
    discount_percentage = cart.get_discount_percentage(request)
    net_total = round(cart.get_net_total(request),2)
    return {
            'cart_items': cart_items,
            'cart_item_count':cart_item_count,
            'cart_total':cart_total,
            'discount_percentage':discount_percentage,
            'net_total':net_total
        }