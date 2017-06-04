from helper import get_cart_data
from django.utils.deprecation import MiddlewareMixin

class CartMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.CART_DATA = get_cart_data(request)