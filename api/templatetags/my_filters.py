from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def translate(text):
    return _(text)