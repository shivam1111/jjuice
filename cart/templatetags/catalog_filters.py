from django import template
import locale

register = template.Library()

@register.filter(name="currency")
def currency(value):
    try:
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL,'')
    loc = locale.localeconv()
    return locale.currency(value or 0.00, loc['currency_symbol'], grouping=True)

