import random
from django import template

register = template.Library()

colors = ['#6200ea','#304ffe ','#2962ff ','#18ffff','#d50000 ','#3F729B ','#7b1fa2','#9933CC ','#0d47a1 ','#2BBBAD ',
         '#00bfa5 ','#64dd17 ','#2e7d32 ','#795548','#f9a825','#7e57c2','#ff6d00']


@register.filter()
def randcolor(parser):
    color = random.choice(colors)
    return color


class FormatColor(template.Node):
    def __init__(self, format_string):
        self.__str__ = format_string

    def render(self, context):
        return self.__str__