from django import template
register = template.Library()

@register.inclusion_tag("flavor_list_view.html")
def flavor_list_view(line):
    return {'line': line }  