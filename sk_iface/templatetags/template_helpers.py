from django import template

register = template.Library()

@register.filter(name='excerpt')
def excerpt(string, arg):
    if len(string) > arg:
        return string[:arg]
    else:
        return string

