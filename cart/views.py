from django.shortcuts import render,get_object_or_404
from django.views import View
from catalog.models import ProductFlavors,ProductAttributeValue
from cart import *
from forms import ProductAddToCartForm
from urllib import quote
from helper import safe_cast,create_aws_url,is_user_business,get_product_variants,get_products_availability,get_cart_data
from django.http import JsonResponse
from django.core.urlresolvers import reverse

class Cart(View):
    _name = "Shopping Cart"
    def get(self,request,template_name="cart.html"):
        name = self._name
        back_url = request.get_full_path()
        back_url = quote(back_url.encode('utf-8'))
        back_url_name = "Cart"
        return render(request,template_name,locals())
    
    def post(self,request,template_name="cart.html"):
        postdata = request.POST.copy()
        name = self._name
        action = postdata.get('action',False)
        back_url = request.get_full_path()
        back_url = quote(back_url.encode('utf-8'))        
        back_url_name = "Cart"
        if action:
            item_id = postdata.get('item_id',False)
            if action == "update" and item_id:
                qty = postdata.get('quantity',False)
                cartitem = get_object_or_404(CartItem,pk=item_id)
                # This means we are updating the cart
                cartitem.quantity = qty
                cartitem.save()                
            if action == "delete" and item_id :
                cartitem = get_object_or_404(CartItem,pk=item_id)
                cartitem.delete()
            if action == "empty_cart":
                cart_items = get_cart_items(request)
                cart_items.delete()
        request.CART_DATA = get_cart_data(request,True)
        return render(request,template_name,locals())

class AddToCart(View):

    def post(self,request,template_name="flavors.html"):
        # add to cart...create the bound form
        status = 200
        response = {
            'error':True,
        }
        postdata = request.POST.copy().dict()
        form = ProductAddToCartForm(request, postdata)
        #check if posted data is valid
        if form.is_valid():
            #add to cart and redirect to cart page
            available_qty,cart_qty,added = add_to_cart(request)
            # if test cookie worked, get rid of it
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                request.session.set_test_cookie()
            # url = urlresolvers.reverse('cart:show_cart')
            response.update({'error': False})
            cart_data = get_cart_data(request)
            cart_data.pop('actual_cart_items')# actual cart items are django objects which are not json serializable hence we remove it
            cart_data.pop('checkout_cart_items')
            cart_data.update({
                'checkout_url':reverse('checkout:checkout',args=[]),
                'authenticated':request.user.is_authenticated(),
                'cart_url': reverse('cart:show_cart', args=[]),
            })
            response.update({
                'data':cart_data,
                'available_qty':available_qty,
                'cart_qty':cart_qty,
                'added':added
            })
            return JsonResponse(data=response, status=status, safe=False)
        else:
            response.update({'msg': "Due to some reason we were unable to update cart"})
            return JsonResponse(data=response, status=status, safe=False)

class QuickCart(View):
    
    def get(self,request,id,template_name="flavor_quick_cart.html"):
        back_url = request.get_full_path()
        flavor_id = int(id) # TypeError and ValueError handled by the decorator
        volume_id = request.GET.get('volume_id',False)
        volume_id = int(volume_id)
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)   
        price  = 0 
        request.session.set_test_cookie()
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page" 
        products = get_product_variants(flavor,volume_id)
        price = flavor.get_price(request.user,current_volume)
        old_price = current_volume.old_price or 0
        return render(request,template_name,locals())
    