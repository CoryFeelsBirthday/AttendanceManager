from django.template.defaultfilters import stringfilter
from urllib.parse import quote
import re
from django import template
from django.conf import settings

register = template.Library()


@register.filter
@stringfilter
@register.filter(is_safe=True)
def url_quote(value):
    return quote(value, safe='')

