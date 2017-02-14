from django import template
register = template.Library()

@register.inclusion_tag("flavor_grid_view.html")
def flavor_grid_view(line):
    return {'line': line }  