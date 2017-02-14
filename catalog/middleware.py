from helper import create_aws_url
from django.utils.deprecation import MiddlewareMixin

class CatalogMiddleware(MiddlewareMixin):
    
    def process_request(self,request):
        from odoo.models import IrConfigParameters,ProductAttributeValue
        
        volumes_available_ids = eval(IrConfigParameters.objects.get_param('attributes_available_ids','[]'))
        volumen_not_available = eval(IrConfigParameters.objects.get_param('attribute_value_ids','[]'))
        volumes_display_ids = set(volumes_available_ids) - set(volumen_not_available)
        volume_objects = ProductAttributeValue.objects.filter(id__in=volumes_display_ids).order_by('name')
        volumes_data = {}
        for i in volume_objects:
            volumes_data.update({
                    i.id:{
                       'name':i.name,
                       'url':create_aws_url(ProductAttributeValue._meta.db_table,str(i.id)) 
                    }
                })
        request.volumes_data = volumes_data        