from django import template
register = template.Library()

@register.inclusion_tag("flavor_grid_view.html")
def flavor_grid_view(line,back_url):
	return {'line': line,'back_url':back_url }