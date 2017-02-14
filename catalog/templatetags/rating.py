from django import template
register = template.Library()

@register.inclusion_tag("rating.html")
def rating(r):
    star = 0
    nostar = 5
    try:
        star = int(r.get('rating',0))
    except (ValueError,TypeError):
        star = 0
    nostar = 5 - star
    return {
            'star':range(star),
            'nostar':range(nostar),
            'title':r.get('title',0),
        }  