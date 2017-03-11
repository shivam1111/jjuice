from django.shortcuts import render,get_object_or_404,HttpResponseRedirect,HttpResponse
from odoo.models import WebsiteBanner,WebsitePolicy,IrConfigParameters,ProductAttributeValue
from models import FlavorConcDetails,ProductVariant,ProductFlavors,FlavorReviews as FlavorReviewModel,S3Object
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import FieldDoesNotExist
from urllib import urlencode
from cart import cart
from cart.forms import ProductAddToCartForm
from django.db import connection
from django.views import View
from helper import safe_cast,create_aws_url
from django.core import urlresolvers
from django.conf import settings
import os

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
        from misc.models import PartnerReviews
        promo_ids = policies = []
        reviews = PartnerReviews.objects.all().order_by('sequence')
        customerreview_banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(customerreview_banner=True)[:1]
        featured_lines = S3Object.objects.filter(is_featured_item=True,attribute_id__in=request.volumes_available_ids)
        if (not request.user.is_authenticated) or (not request.user.odoo_user.partner_id.classify_finance) or (request.user.odoo_user.partner_id.classify_finance == 'website'):
            promo_ids = eval(IrConfigParameters.objects.get_param('promo_non_business_ids','[]'))
        else :
            promo_ids = eval(IrConfigParameters.objects.get_param('promo_business_ids','[]'))
        policies = WebsitePolicy.objects.filter(id__in=promo_ids).order_by('sequence')[:3]
        lines_list = []
        if featured_lines.exists():
            for line in featured_lines:
                try:
                    lines_list.append(FlavorConcDetails.objects.get(
                                                          flavor_id = line.flavor_id,
                                                          tab_id__vol_id=line.attribute_id,
                                                          tab_id__visible_all_customers=True,
                                                          tab_id__consumable_stockable = 'product',
                                                          tab_id__active = True                    
                                                    ))
                except FlavorConcDetails.DoesNotExist:
                    pass
        if banner_record.exists():
            customerreview_banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))
        return render(request,"index.html",locals())        

class Volume(View):

    @safe_cast
    def get(self,request,id,template_name="volumes.html"):
        volume_id = int(id) # TypeError and ValueError handled by the decorator
        assert volume_id in request.volumes_data.keys() , "You are not allowed to access this page"
        volume_data = request.volumes_data[volume_id]
        name = volume_data['name']
        sort_by = request.GET.get('sort_by','default')
        lines_list = FlavorConcDetails.objects.filter(
                                                      tab_id__vol_id=volume_id,
                                                      tab_id__visible_all_customers=True,
                                                      tab_id__consumable_stockable = 'product',
                                                      tab_id__active = True
                                                    )

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
        price = old_price = 0
        name = flavor.name
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to acces this page"
        form = ProductAddToCartForm(request=request, label_suffix=':') 
        # set the test cookie on our first GET request 
        request.session.set_test_cookie()
        products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id,product_tmpl_id__type="product").distinct('conc_id__id')
        price = flavor.get_price(request.user,current_volume) 
        old_price = current_volume.old_price or 0
        return render(request,template_name,locals())
    
    @safe_cast
    def post(self,request,id,template_name="flavors.html"): 
        from cart.forms import ProductAddToCartForm
        # add to cart...create the bound form
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        #check if posted data is valid
        if form.is_valid():
            #add to cart and redirect to cart page
            cart.add_to_cart(request)
            # if test cookie worked, get rid of it
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            url = urlresolvers.reverse('cart:show_cart')
            return HttpResponseRedirect(url)
        flavor_id = int(postdata.get('flavor_id',False)) # TypeError and ValueError handled by the decorator
        volume_id = int(postdata.get('volume_id',False))
        conc_id = postdata.get('conc_id',False)
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)
        price = old_price = 0
        name = flavor.name
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page"        
        products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id,product_tmpl_id__type="product").distinct('conc_id__id')
        price = flavor.get_price(request.user,current_volume) 
        old_price = current_volume.old_price        
        request.session.set_test_cookie()
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
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to access this page" 
        products = flavor.flavor_product_variant_ids.filter(vol_id=volume_id).distinct('conc_id__id')
        price = flavor.get_price(request.user,current_volume)
        old_price = current_volume.old_price
        return render(request,template_name,locals())         

class FlavorReview(View):
    
    def post(self,request):
        postdata = request.POST.copy()
        flavor_id = postdata.get('flavor_id',False)
        partner = request.user.odoo_user.partner_id
        flavor = get_object_or_404(ProductFlavors,id=flavor_id)
        if request.user.is_authenticated and flavor_id:
            if not partner.review_ids.filter(flavor_id =flavor_id ).exists():
                FlavorReviewModel.objects.create(**{
                        'partner_id':partner,
                        'flavor_id':flavor,
                        'title':postdata.get('title',"No Title"),
                        'name':postdata.get('name',partner.name),
                        'email':postdata.get('email',partner.email),
                        'description':postdata.get('description',"-"),
                        'rating':postdata.get('rating',"3")
                })
        url_flavor = flavor.get_url()
        qstr = urlencode({'volume_id':postdata.get('volume_id',"")})
        url = "?".join([url_flavor,qstr])
        return HttpResponseRedirect(url)
        
                
                
    