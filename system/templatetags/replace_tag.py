from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter(name='myreplace')
def myreplace(value):
    text = value.replace('\n','<BR>')
    return mark_safe(text)
    