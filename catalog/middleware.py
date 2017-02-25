from helper import create_aws_url
from django.utils.deprecation import MiddlewareMixin
from collections import OrderedDict

class CatalogMiddleware(MiddlewareMixin):
    
    def process_request(self,request):
        from odoo.models import IrConfigParameters,ProductAttributeValue
        volumes_available_ids = []
        if (not request.user.is_authenticated) or (not request.user.odoo_user.partner_id.classify_finance) or (request.user.odoo_user.partner_id.classify_finance == 'website'):
#             eval(IrConfigParameters.objects.get_param('attributes_available_ids','[]'))
            volumes_available_ids = eval(IrConfigParameters.objects.get_param('attribute_value_ids','[]'))
        else :
            volumes_available_ids = eval(IrConfigParameters.objects.get_param('attributes_available_ids','[]'))
        volume_objects = ProductAttributeValue.objects.filter(id__in=volumes_available_ids).order_by('sequence')
        volumes_data = OrderedDict()
        for i in volume_objects:
            volumes_data.update({
                    i.id:{
                       'name':i.name,
                       'url':create_aws_url(ProductAttributeValue._meta.db_table,str(i.id)) 
                    }
                })
        request.volumes_data = volumes_data