from django import template

register = template.Library()

@register.filter
def formateo_precio(value):
    if value is None:
        return ''
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value
    formatted_price = "${:,.0f}".format(value).replace(',', '.')
    return formatted_price