from django import template
register = template.Library()

@register.inclusion_tag("flavor_list_view.html")
def flavor_list_view(line,back_url):
    return {'line': line,'back_url':back_url }  