from django import template
from core.models import Gymnast, Score
from weekly_gameplay.models import Average
register = template.Library()
@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__

# basically just fixes the green around the input boxes when password incorrect
@register.filter
def input_class(bound_field):
    css_class = ''
    if bound_field.form.is_bound:
        if bound_field.errors:
            css_class = 'is-invalid'
        elif field_type(bound_field) != 'PasswordInput':
            css_class = 'is-valid'
    return 'form-control {}'.format(css_class)

@register.filter
def get_fields(obj):
    if obj:
        return [(field.name, field.value_to_string(obj)) for field in obj._meta.fields]

@register.filter
def from_gymnast(averages, gymnast):
    return averages.filter(gymnast=gymnast)

@register.filter
def is_from_event(average, event):
    if average.event == event:
        return True
    else:
        return False
    

    

# @register.filter
# def num_gymnasts(obj, event):
#     num = 0
#     if obj:
#         for x in obj.filter(event=event):
#             num += 1
#         return num