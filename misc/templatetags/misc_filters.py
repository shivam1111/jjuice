from django import template
from image_process import image_resize_image
register = template.Library()

@register.filter(name="resize_image_230X319")
def resize_image_230X319(value):
    return image_resize_image(value, (230,319), encoding="base64", filetype=None, avoid_if_small=True)

