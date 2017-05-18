from django import template

register = template.Library()

@register.simple_tag
def get_class_responsive(no_items):
    return 12/no_items