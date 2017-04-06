from django.shortcuts import render,get_object_or_404,HttpResponseRedirect,HttpResponse
from django.http import JsonResponse
from odoo.models import WebsiteBanner,WebsitePolicy,IrConfigParameters,ProductAttributeValue
from models import FlavorConcDetails,ProductVariant,ProductFlavors,FlavorReviews as FlavorReviewModel,S3Object
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from django.db.models import FieldDoesNotExist,Q
from urllib import urlencode,quote,unquote
from cart import cart
from cart.forms import ProductAddToCartForm
from django.db import connection
from django.views import View
from helper import safe_cast,create_aws_url,is_user_business,get_product_variants
from django.core import urlresolvers
from django.conf import settings
from odoo_helpers import OdooAdapter
import os,requests
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

_PER_PAGE_OPTIONS = [
        (10,'10'),
        (20,'20'),
        (30,'30')
    ]

_SORT_BY = [
    ('name','Name'),
    ('-create_date','Latest'),
]

class Index(View):
    def get(self,request,template_name="index.html"):
        from misc.models import PartnerReviews
        promo_ids = policies = []
        reviews = PartnerReviews.objects.all().order_by('sequence')
        customerreview_banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(customerreview_banner=True)[:1]
        featured_lines = S3Object.objects.filter(is_featured_item=True,attribute_id__in=request.volumes_available_ids)
        if is_user_business(request.user):
            promo_ids = eval(IrConfigParameters.objects.get_param('promo_non_business_ids','[]'))
        else :
            promo_ids = eval(IrConfigParameters.objects.get_param('promo_business_ids','[]'))
        policies = WebsitePolicy.objects.filter(id__in=promo_ids).order_by('sequence')[:3]
        lines_list = []
        if featured_lines.exists():
            for line in featured_lines:
                try:
                    lines_list.append((line.flavor_id,line.attribute_id))
                except FlavorConcDetails.DoesNotExist:
                    pass
        if banner_record.exists():
            customerreview_banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))
        return render(request,"index.html",locals())        

class Volume(View):

    def get(self,request,id,view='form',template_name="volumes_grid.html"):
        volume_id = int(id) # TypeError and ValueError handled by the decorator
        assert volume_id in request.volumes_data.keys() , "You are not allowed to access this page"
        if view == 'list':
            template_name = "volumes_list.html"
        volume_data = request.volumes_data[volume_id]
        
        name = volume_data['name']
        sort_by = request.GET.get('sort_by','name')
        product_variants = ProductVariant.objects.filter(
                                                active=True,
                                                vol_id = volume_id,
                                                product_tmpl_id__type = 'product',
                                                product_tmpl_id__sale_ok=True,
                                                tab_id__vol_id=volume_id,
                                                tab_id__visible_all_customers=True,
                                                tab_id__consumable_stockable = 'product',
                                                tab_id__active = True).distinct('flavor_id__id')
        flavor_ids = set(map(lambda x: x.flavor_id.id,product_variants))
        flavors = ProductFlavors.objects.filter(id__in=flavor_ids).order_by(sort_by)
        page = int(request.GET.get('page',1))
        per_page = int(request.GET.get('per_page',30))
        paginator = Paginator(flavors, per_page)
        try:
            flavor_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            flavor_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            flavor_lines = paginator.page(paginator.num_pages)
        per_page_options = _PER_PAGE_OPTIONS
        sort_options = _SORT_BY
        back_url = request.get_full_path()
        back_url = quote(back_url.encode('utf-8'))
        range_pages = range(paginator.num_pages)
        return render(request,template_name,locals())

class Flavor(View):
    
    @safe_cast
    def get(self,request,id,template_name="flavors.html"):
        flavor_id = int(id) # TypeError and ValueError handled by the decorator
        volume_id = request.GET.get('volume_id',False)
        volume_id = int(volume_id)
        back_url = request.GET.get('back',"/")
        back_url = unquote(back_url.encode('utf-8'))
        conc_id = request.GET.get('conc_id',False) and int(request.GET['conc_id']) or False
        flavor = get_object_or_404(ProductFlavors, pk=flavor_id)
        current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)
        price = old_price = 0
        name = flavor.name
        assert volume_id and (volume_id in request.volumes_data.keys()) , "You are not allowed to acces this page"
        form = ProductAddToCartForm(request=request, label_suffix=':') 
        # set the test cookie on our first GET request 
        request.session.set_test_cookie()
        products = get_product_variants(flavor,volume_id)
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
        products = get_product_variants(flavor,volume_id)
        price = flavor.get_price(request.user,current_volume) 
        old_price = current_volume.old_price        
        request.session.set_test_cookie()
        back_url = request.GET.get('back',"/")
        back_url = unquote(back_url.encode('utf-8'))
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

class Search(View):
    
    def get(self,request,template_name = "search.html"):
        lines_list = []
        search = request.GET.get('search',False)
        page = int(request.GET.get('page',1))
        per_page = int(request.GET.get('per_page',20))
        if search:
            lines_list = ProductVariant.objects.filter(
                                                  Q(product_tmpl_id__name__icontains = search) |
                                                  Q(tab_id__name__icontains=search) |
                                                  Q(vol_id__name__icontains = search)
                                              ).filter( 
                                                  Q(product_tmpl_id__sale_ok=True),
                                                  Q(product_tmpl_id__type = 'product'),
                                                  Q(active=True),                                 
                                                  Q(vol_id__in=request.volumes_available_ids) ,                
                                                  Q(tab_id__visible_all_customers=True) , 
                                                  Q(tab_id__consumable_stockable = 'product') ,
                                                  Q(tab_id__active = True),
                                                  Q(tab_id__vol_id__in=request.volumes_available_ids)                    
                                              ).distinct('flavor_id__id','vol_id__id')
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
        search_banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(search_banner=True)[:1]
        back_url = "?".join([request.path,urlencode({
                'search':search,
                'per_page':per_page,
                'page':page
            })])
        back_url = quote(back_url.encode("utf-8"))
        if banner_record.exists():
            search_banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))        
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
        
                
                
    