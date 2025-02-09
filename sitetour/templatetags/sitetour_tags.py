from django import template
from sitetour.utils import menu

register = template.Library()


@register.simple_tag()
def get_menu():
    return menu

