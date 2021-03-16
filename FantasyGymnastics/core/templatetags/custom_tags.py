from django import template
from core.models import Gymnast, Score, League, FantasyTeam, LineUp
from weekly_gameplay.models import Average
from scraper.Scraper import Scraper, ScraperConstants
from datetime import datetime
import decimal

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


#######
@register.filter
def has_event_score(scores, event):
    if scores.filter(event=event).exists():
        return True
        
@register.filter
def scores_from_week(gymnast, week):
    return Score.objects.filter(gymnast=gymnast, week=week)

@register.filter
def get_highest_event_score(score, event):
    scores = score.filter(event=event)
    highest = scores.first()
    for s in scores:
        if s.score > highest.score:
            highest = s
    return highest

@register.filter
def all_averages(gymnast):
    return Average.objects.filter(gymnast=gymnast)

@register.filter
def event_average(gymnast, event):
    average = Average.objects.filter(gymnast=gymnast, event=event)
    if len(average):
        return Average.objects.get(gymnast=gymnast, event=event)
    
@register.filter
def current_week(lineup, week):
    return lineup.filter(week=week)

@register.filter
def event(lineup, event):
    if lineup.filter(event=event).exists():
        return lineup.get(event=event)

@register.filter
def actual_lineup_score(lineup):
    total = decimal.Decimal(0.00)
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
def predicted_lineup_score(lineup):
    total = decimal.Decimal(0.00)
    score_ids = []
    scores_and_averages = []
    teams_competed = Score.objects.filter(week=lineup.week).values('gymnast__team').distinct()
    averages = Average.objects.filter(gymnast__in=lineup.gymnasts.all(), event=lineup.event).order_by('-score').exclude(gymnast__team__in=teams_competed)
    for gymnast in lineup.gymnasts.all():
        gymnast_scores = Score.objects.filter(gymnast=gymnast, event=lineup.event, week=lineup.week)
        if gymnast_scores.exists():
            gymnasts_highest = gymnast_scores.first()
            for score in gymnast_scores:
                if score.score > gymnasts_highest.score:
                    gymnasts_highest = score
            score_ids.append(gymnasts_highest.id)
    scores = Score.objects.filter(id__in=score_ids).order_by('-score')
    for score in scores:
        scores_and_averages.append(score.score)
    for average in averages:
        scores_and_averages.append(average.score)
   
    if len(scores_and_averages) > int(lineup.team.league.event_count_size):
        scores_and_averages.sort(reverse=True)
        scores_and_averages = scores_and_averages[:int(lineup.team.league.event_count_size)]
    for score in scores_and_averages:
        total += score
    return round(total,2)

@register.filter
def actual_team_score(lineups):
    total = decimal.Decimal(0.00)
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

@register.filter
def predicted_team_score(lineups):
    total = decimal.Decimal(0.00)
    for lineup in lineups:
        score_ids = []
        scores_and_averages = []
        teams_competed = Score.objects.filter(week=lineup.week).values('gymnast__team').distinct()
        averages = Average.objects.filter(gymnast__in=lineup.gymnasts.all(), event=lineup.event).order_by('-score').exclude(gymnast__team__in=teams_competed)
        for gymnast in lineup.gymnasts.all():
            gymnast_scores = Score.objects.filter(gymnast=gymnast, event=lineup.event, week=lineup.week)
            if gymnast_scores.exists():
                gymnasts_highest = gymnast_scores.first()
                for score in gymnast_scores:
                    if score.score > gymnasts_highest.score:
                        gymnasts_highest = score
                score_ids.append(gymnasts_highest.id)
        scores = Score.objects.filter(id__in=score_ids).order_by('-score')
        for score in scores:
            scores_and_averages.append(score.score)
        for average in averages:
            scores_and_averages.append(average.score)
    
        if len(scores_and_averages) > int(lineup.team.league.event_count_size):
            scores_and_averages.sort(reverse=True)
            scores_and_averages = scores_and_averages[:int(lineup.team.league.event_count_size)]
        for score in scores_and_averages:
            total += score
    return round(total,2)

@register.filter
def team_has_competed(gymnast, week):
    gymnasts = Gymnast.objects.filter(team=gymnast.team)
    if Score.objects.filter(gymnast__in=gymnasts, week=week).exists():
        return True
    return False

@register.filter
def has_users_team(matchup, user):
    if matchup.team1.user == user or matchup.team2.user == user:
        return "active"
    else:
         return ""
        
@register.filter
def meets(scores):
    meets = []
    for meet in scores.values('meet').order_by('-date').distinct():
       meets.append({'name' : meet['meet'], 'date' : scores.filter(meet=meet['meet']).first().date})
    return meets

@register.filter
def meet_scores(scores, meet):
    print(meet['name'])
    events = ['FX', 'PH', 'SR', 'VT', 'PB', 'HB']
    event_scores = []
    for event in events:
        if scores.filter(meet=meet['name'], event=event).exists():
            event_scores.append(round(scores.get(meet=meet['name'], event=event).score,2))
        else:
            event_scores.append(0.00)
    return event_scores

@register.filter
def has_team_in_league(user, league):
    if FantasyTeam.objects.filter(league=league, user=user).exists():
        return True
    return False

@register.filter
def waiting_to_join(user, league):
    if user in league.requested_to_join.all():
        return True
    return False

@register.filter
def competes_this_week(gymnast, teams):
    if gymnast.team in teams:
        return True
    return False

@register.filter
def get_current_matchups(matchups, current_week):
    return matchups.filter(week=current_week)

@register.filter
def in_lineup_current_week(gymnast, team):
    scraper = Scraper()
    current_week = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.now().year)['week'])
    return gymnast.LineUp.filter(week=current_week, team=team).exists()
