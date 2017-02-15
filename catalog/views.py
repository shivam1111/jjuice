from django.shortcuts import render,get_object_or_404
from odoo.models import WebsiteBanner,WebsitePolicy,IrConfigParameters,ProductAttributeValue
from models import FlavorConcDetails,ProductVariant,ProductFlavors
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import FieldDoesNotExist
import urlparse
from django.db import connection
from django.views import View
from helper import safe_cast,get_price

_PER_PAGE_OPTIONS = [
        (10,'10'),
        (20,'25'),
        (30,'30')
    ]

_SORT_BY = [
    ('default','Recommended'),
    ('-create_date','Latest')
]

class Index(View):
    def get(self,request,template_name="index.html"):
        banners = policies = []
        if not request.user.is_authenticated():
            banners = WebsiteBanner.objects.all().order_by('sequence')
            policies = WebsitePolicy.objects.all().order_by('sequence')[:3]
        return render(request,"index.html",{'banners':banners,'policies':policies})        

class Volume(View):

    @safe_cast
    def get(self,request,id,template_name="volumes.html"):
        volume_id = int(id) # TypeError and ValueError handled by the decorator
        assert volume_id in request.volumes_data.keys() , "You are not allowed to acces this page"
        name = request.volumes_data[volume_id]['name']
        sort_by = request.GET.get('sort_by','default')
        if request.user.is_authenticated():
            # If the user is logged the behaviour goes here
            pass            
        else:
            lines_list = FlavorConcDetails.objects.filter(tab_id__vol_id=volume_id,
                                                          tab_id__visible_all_customers=True,
                                                          tab_id__consumable_stockable = 'product')

        try:
            lines_list.order_by(sort_by)
        except FieldDoesNotExist as e:
            sort_by = "default"
        page = int(request.GET.get('page',1))
        per_page = int(request.GET.get('per_page',10))
        paginator = Paginator(lines_list, per_page)
        try:
            lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            lines = paginator.page(paginator.num_pages)
        per_page_options = _PER_PAGE_OPTIONS
        sort_options = _SORT_BY
        return render(request,template_name,locals())

class Flavor(View):
    
    @safe_cast
    def get(self,request,id,template_name="flavors.html"):
        flavor_id = int(id) # TypeError and ValueError handled by the decorator
        volume_id = request.GET.get('volume_id',False)
        volume_id = int(volume_id)
        conc_id = request.GET.get('conc_id',False) and int(request.GET['conc_id']) or False
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)
        next_id =  request.GET.get('next_id','')
        previous_id = request.GET.get('previous_id','')
        price = old_price = 0
        is_authenticated = request.user.is_authenticated()
        if next_id:
            next_id = int(next_id)
        if previous_id:
            previous_id = int(previous_id)
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to acces this page"
        if is_authenticated:
            # If the user is logged the behaviour goes here
            pass            
        else:
#             volumes = flavor.flavor_product_variant_ids.values_list('vol_id__id','vol_id__name').distinct('vol_id__id')
            products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id).distinct('conc_id__id')
            price = get_price(is_authenticated,current_volume) 
            old_price = current_volume.old_price
        return render(request,template_name,locals()) 

class FlavorQuickView(View):
    
    @safe_cast
    def get(self,request,id,template_name="flavor_quick_view.html"):
        flavor_id = int(id) # TypeError and ValueError handled by the decorator
        volume_id = request.GET.get('volume_id',False)
        volume_id = int(volume_id)
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)   
        price  = 0 
        is_authenticated = request.user.is_authenticated()   
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page" 
        if is_authenticated:
            # If the user is logged the behaviour goes here
            pass            
        else:
            products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id).distinct('conc_id__id')
            price = get_price(is_authenticated,current_volume)
            old_price = current_volume.old_price
        return render(request,template_name,locals())         
                
                
    