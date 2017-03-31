from django import template
from odoo.models import ProductAttributeValue
from django.shortcuts import get_object_or_404
register = template.Library()

@register.inclusion_tag("flavor_list_view.html")
def flavor_list_view(flavor,volume_id,name,back_url):
    # name is volume name
    if isinstance(volume_id,ProductAttributeValue):
    	current_volume = volume_id
    else:	
    	current_volume = get_object_or_404(ProductAttributeValue, pk=volume_id)    
    return {'flavor_id': flavor,'current_volume':current_volume,'back_url':back_url }