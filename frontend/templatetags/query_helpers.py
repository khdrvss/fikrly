from django import template
from urllib.parse import urlencode

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_without(context, key):
    request = context.get('request')
    if not request:
        return ''
    params = request.GET.copy()
    params.pop(key, None)
    return params.urlencode()


@register.simple_tag(takes_context=True)
def remove_category_query(context, cat_id):
    request = context.get('request')
    if not request:
        return ''
    params = request.GET.copy()
    categories = params.get('categories', '')
    if not categories:
        return params.urlencode()
    cats = [c for c in categories.split(',') if c]
    cats = [c for c in cats if c != str(cat_id)]
    if cats:
        params['categories'] = ','.join(cats)
    else:
        params.pop('categories', None)
    return params.urlencode()
