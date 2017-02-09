from django.shortcuts import render
from odoo.models import WebsiteBanner,WebsitePolicy
import urlparse

def index(request,template_name="catalog/index.html"):
    banners = map(lambda x:{
                'name':x.s3_object_id.store_fname,'url':x.s3_object_id.url
            },
            WebsiteBanner.objects.all().exclude(s3_object_id=None).order_by('sequence'))
    policies = map(lambda x:{
                'name':x.name,
                'url':x.s3_object_id.url,
                'description':x.description or '',
            },
            WebsitePolicy.objects.all().exclude(s3_object_id=None).order_by('sequence')[:3])
     
    return render(request,"index.html",locals())