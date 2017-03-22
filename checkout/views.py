from django.shortcuts import render,get_object_or_404
from django.views import View
from helper import safe_cast
from urllib import quote
import os
from django.conf import settings
from catalog.models import S3Object
from odoo.models import Country,State
from helper import create_aws_url

country_ids = Country.objects.all()

class Checkout(View):
    _name = "Checkout"
    
    def get(self,request,template_name="checkout.html"):
        name = self._name
        
        back_url = request.GET.get('back_url',False)
        back_url_name = request.GET.get('back_url_name','No Name')
        if back_url: 
            back_url = quote(back_url.encode('utf-8'))
        checkout_banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(checkout_banner=True)[:1]
        countries_list  = map(lambda x:(x.id,x.name),country_ids)
        address = False
        if banner_record.exists():
            checkout_banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))
        if request.user.is_authenticated:
            partner = request.user.odoo_user.partner_id
            address = {
                    'name':partner.name,
                    'is_company':partner.is_company,
#                     'street':partner.street,
#                     'country_id':partner.country_id.id,
#                     'street2':partner.street2,
                    'city':partner.city,
#                     'state'
                }            
        return render(request,template_name,locals())
    
    def post(self,request,template_name="checkout.html"):
        return render(request,template_name,locals().update(countries_list))

