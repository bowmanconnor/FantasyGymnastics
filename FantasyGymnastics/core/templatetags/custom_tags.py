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
def lineup_score(lineup):
    print(lineup.event)
    total = 0
    scores = []
    for gymnast in lineup.gymnasts.all():
        gymnast_scores = Score.objects.filter(gymnast=gymnast, event=lineup.event, week=lineup.week)
        if gymnast_scores.exists():
            gymnasts_highest = gymnast_scores.first()
            for score in gymnast_scores:
                if score.score > gymnasts_highest.score:
                    gymnasts_highest = score
            scores.append(gymnasts_highest.score)
    if len(scores) > int(lineup.team.league.event_count_size):
        scores.sort(reverse=True)
        scores = scores[:int(lineup.team.league.event_count_size)]
    for score in scores:
        total += score
    return round(total,2)

  
@register.filter
def team_score(lineups):
    total = 0
    for lineup in lineups:
        scores = []
        for gymnast in lineup.gymnasts.all():
            gymnast_scores = Score.objects.filter(gymnast=gymnast, event=lineup.event, week=lineup.week)
            if gymnast_scores.exists():
                gymnasts_highest = gymnast_scores.first()
                for score in gymnast_scores:
                    if score.score > gymnasts_highest.score:
                        gymnasts_highest = score
                scores.append(gymnasts_highest.score)
        if len(scores) > int(lineup.team.league.event_count_size):
            scores.sort(reverse=True)
            scores = scores[:int(lineup.team.league.event_count_size)]
        for score in scores:
            total += score
    return round(total,2)