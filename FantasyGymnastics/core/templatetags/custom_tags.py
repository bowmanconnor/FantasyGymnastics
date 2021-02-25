from django import template
from core.models import Gymnast, Score
from weekly_gameplay.models import Average
from scraper.Scraper import Scraper, ScraperConstants
from datetime import datetime
register = template.Library()

# Used in bootstrap form stuff
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

# Used in view matchup and gymnast search
@register.filter
def from_gymnast(obj, gymnast):
    return obj.filter(gymnast=gymnast)

@register.filter
def has_event_score(obj, event):
    if obj.filter(event=event).exists():
        return True
      
@register.filter
def get_highest_event_score(score, event):
    scores = score.filter(event=event)
    highest = scores.first()
    for s in scores:
        if s.score > highest.score:
            highest = s
    return highest

@register.filter
def current_week(lineup, week):
    return lineup.filter(week=week)

    
@register.filter
def total_score(scores, team):
    scores = scores.filter(team=team)
