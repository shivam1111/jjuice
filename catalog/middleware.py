from helper import create_aws_url
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from collections import OrderedDict
from helper import is_user_business

class CatalogMiddleware(MiddlewareMixin):
    
    def process_request(self,request):
        from odoo.models import IrConfigParameters,ProductAttributeValue,country_ids
        volumes_available_ids = []
        if is_user_business(request.user) :
            volumes_available_ids = eval(IrConfigParameters.objects.get_param('attributes_available_ids','[]'))
        else:
            volumes_available_ids = eval(IrConfigParameters.objects.get_param('attribute_value_ids', '[]'))
        volume_objects = ProductAttributeValue.objects.filter(id__in=volumes_available_ids).order_by('sequence')
        volumes_data = OrderedDict()
        for i in volume_objects:
            volumes_data.update({
                    i.id:{
                       'name':i.name,
                       'image_url':create_aws_url(ProductAttributeValue._meta.db_table,str(i.id)),
                       'banner_url': create_aws_url(ProductAttributeValue.banner_key,str(i.id)),
                       'category_url':i.file_name_category and create_aws_url(ProductAttributeValue.category_key,str(i.id)) or False,
                    }
                })
        request.volumes_data = volumes_data
        request.volumes_available_ids = volumes_available_ids
        request.country_ids = country_ids
        request.agechecker = {
            'key':settings.AGECHECKER_KEY,
            'name':settings.AGECHECKER_NAME
        }