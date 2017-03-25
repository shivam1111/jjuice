from django import template

register = template.Library()

@register.simple_tag
def call_method(obj, method_name, **kwargs):
    method = getattr(obj, method_name)
    return method(**kwargs)

@register.simple_tag
def flavor_get_image_url(obj,volume_id):
    return obj.get_image_url(volume_id)