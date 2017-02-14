from django import template
register = template.Library()

@register.inclusion_tag("options.html")
def options(options,active_option=False):
    return {'active_option': active_option,'options':options }  