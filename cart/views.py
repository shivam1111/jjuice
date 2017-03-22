from django.shortcuts import render,get_object_or_404
from django.views import View
from models import CartItem
from catalog.models import ProductFlavors,ProductAttributeValue
from cart import *
from helper import safe_cast
from urllib import quote

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
        return render(request,template_name,locals())

class QuickCart(View):
    
    def get(self,request,id,template_name="flavor_quick_cart.html"):
        flavor_id = int(id) # TypeError and ValueError handled by the decorator
        volume_id = request.GET.get('volume_id',False)
        volume_id = int(volume_id)
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)   
        price  = 0 
        request.session.set_test_cookie()
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page" 
        products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id,product_tmpl_id__type="product",product_tmpl_id__sale_ok=True).distinct('conc_id__id')
        price = flavor.get_price(request.user,current_volume)
        old_price = current_volume.old_price or 0
        return render(request,template_name,locals())
    