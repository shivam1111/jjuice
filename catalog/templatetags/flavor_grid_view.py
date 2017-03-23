from django import template
from odoo.models import ProductAttributeValue
register = template.Library()

@register.inclusion_tag("flavor_grid_view.html")
def flavor_grid_view(flavor,volume_id,name,back_url):
	# name is volume name
	return {'flavor_id': flavor,'name':name,'volume_id':volume_id,'back_url':back_url }