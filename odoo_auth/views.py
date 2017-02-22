from django.views import View
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from odoo.models import Partner
from odoo_helpers import OdooAdapter
import base64

class UploadProfileImage(View):
    
    def post(self,request):
        postdata = request.POST.copy()
        image =  request.FILES.get('image',False)
        image_base64 = base64.encodestring(image.read())
        odoo_adapter = OdooAdapter()
        if image:
            odoo_adapter.execute_method('res.partner','write',[request.user.odoo_user.partner_id.id,{'image':image_base64}])
        return HttpResponse(image_base64)
        