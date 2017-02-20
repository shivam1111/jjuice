from django.shortcuts import render
from django.views import View
from cart import *

class Cart(View):

    def get(self,request,template_name="cart/cart.html"):
        name = "Shopping Cart"
        return render(request,template_name,locals())