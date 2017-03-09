from django.core.cache import cache
from django import template
from image_process import image_resize_image
from PIL import Image
import requests
from StringIO import StringIO
import base64
register = template.Library()


@register.simple_tag
def cache_resize_image_url(key,height,width):
    # Key can be a url or anything unique
    image_cache = cache.get(key)
    if image_cache:
        return image_cache
    else:
        response = requests.get(key)
        base64_source = base64.b64encode(response.content)
        image_cache = image_resize_image(base64_source, (height,width), encoding='base64', filetype=None, avoid_if_small=True)
        cache.set(key, image_cache)
    return image_cache