from django import template
from decimal import Decimal
from math import floor

register = template.Library()


def render_asset(amount, asset):
    n = 10**asset.decimal_places
    m = floor(amount * Decimal(n))
    i = 0
    digits = ""
    while m > 0 or i < asset.decimal_places + 1:
        digits = chr(ord("0") + m % 10) + digits
        i += 1
        m //= 10
        if i == asset.decimal_places:
            digits = "." + digits
    return f"{digits} {asset.code}"


register.filter("asset", render_asset)
