from django import template

register = template.Library()

@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)

@register.simple_tag
def flavor_get_image_url(obj,volume_id):
    return obj.get_image_url(volume_id)