from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from core.models import League, FantasyTeam, Gymnast, LineUp, Score
from django.views.generic import UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import NewMatchupForm
from .models import Matchup, Average
from scraper.Scraper import Scraper, ScraperConstants
import datetime 
import random 
from core.views import teams_competing_this_week
from pytz import timezone

# Create your views here.

def add_gymnast_to_roster(request, team_pk, gymnast_pk):
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    team = get_object_or_404(FantasyTeam, pk=team_pk)
    team.roster.add(gymnast)
    league = team.league
    league.drafted.add(gymnast)
    print('-------------------------------------------------')
    print(str(team) + " drafted " + str(gymnast))
    print('-------------------------------------------------')
    return redirect('view_team', pk=team_pk)

def remove_gymnast_from_roster(request, team_pk, gymnast_pk):
    scraper = Scraper()
    current_week = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['week'])

    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    team = get_object_or_404(FantasyTeam, pk=team_pk)
    team.roster.remove(gymnast)
    league = team.league
    lineups = LineUp.objects.filter(team=team, week=current_week)
    for lineup in lineups:
        lineup.gymnasts.remove(gymnast)
    league.drafted.remove(gymnast)
    return redirect('view_team', pk=team_pk)

def add_gymnast_to_lineup(request, lineup_pk, gymnast_pk):
    lineup = get_object_or_404(LineUp, pk=lineup_pk)
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    lineup.gymnasts.add(gymnast)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_gymnast_from_lineup(request, lineup_pk, gymnast_pk):
    lineup = get_object_or_404(LineUp, pk=lineup_pk)
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    lineup.gymnasts.remove(gymnast)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def create_matchup(request, league_pk):
    if request.method == 'POST':
        form = NewMatchupForm(request.POST)
        if form.is_valid():
            matchup = form.save(commit=False)
            if Matchup.objects.filter(team1=matchup.team1, week=matchup.week).exists() or Matchup.objects.filter(team2=matchup.team2, week=matchup.week).exists() or Matchup.objects.filter(team1=matchup.team2, week=matchup.week).exists() or Matchup.objects.filter(team2=matchup.team1, week=matchup.week).exists() or matchup.team1 == matchup.team2:
                print("DUPLICATE")
            else:
                matchup.league = matchup.team1.league
                matchup.save()
            return redirect('league_standings', pk=league_pk)
    else:
        form = NewMatchupForm()
        form.fields['team1'].queryset = FantasyTeam.objects.filter(league=league_pk)
        form.fields['team2'].queryset = FantasyTeam.objects.filter(league=league_pk)
    return render(request, 'weekly_gameplay/create_matchup.html', {'form': form})

class ViewMatchup(DetailView):
    model = Matchup
    template_name = 'weekly_gameplay/view_matchup.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'matchup'

    def get_context_data(self, **kwargs):
        scraper = Scraper()
        context = super().get_context_data(**kwargs)
        if context['object'].team2.user == self.request.user:
            context['team1'] = context['object'].team2
            context['team2'] = context['object'].team1
        else: 
            context['team1'] = context['object'].team1
            context['team2'] = context['object'].team2
        gymnasts = (Gymnast.objects.filter(LineUp__in=(LineUp.objects.filter(team=context['team1'], week=context['object'].week).all() | LineUp.objects.filter(team=context['team2'], week=context['object'].week).all())) | Gymnast.objects.filter(id__in=(context['team1'].roster.all() | context['team2'].roster.all()))).distinct()
        current_week = int(scraper.get_current_and_max_week(ScraperConstants.Men, datetime.datetime.now().year)['week'])

        context['current_week'] = current_week
        context['teams_competing'] = teams_competing_this_week()
        context['meet_started'] = {}
        weeks = scraper.get_year_weeks(ScraperConstants.Men, datetime.datetime.now().year)
        date = [week for week in weeks if int(week['wk']) == int(context['object'].week)][0]['date']
        schedule = scraper.get_schedule(ScraperConstants.Men, date)
        # Loops through every meet day this week
        for day in schedule:
            # Loops through every meet on day
            for meet in schedule[day]['meets']:
                # Loops through gymnasts 
                for gymnast in gymnasts:
                    # Checks if gymnasts team is in this meet
                    if gymnast.team in str(meet['home_teams']) or gymnast.team in str(meet['away_teams']):
                        # Checks if this is gymnasts first meet of week
                        if gymnast.name not in context['meet_started']:
                            # Meet start datetime
                            meet_datetime = datetime.datetime.strptime(str(meet['d']) + " " + str(meet['time']), "%Y-%m-%d %H:%M:%S")
                            # Current datetime (eastern because thats what RTN uses)
                            now = datetime.datetime.now(timezone('US/Eastern'))
                            if now.date() > meet_datetime.date():
                                context['meet_started'][gymnast.name] = True
                            elif now.date() == meet_datetime.date():
                                if meet_datetime.time() != datetime.time(0, 0, 0):
                                    if now.time() > meet_datetime.time():
                                        context['meet_started'][gymnast.name] = True
                                else:
                                    if now.time() >= datetime.time(12, 0, 0):
                                        context['meet_started'][gymnast.name] = True
                            else:
                                context['meet_started'][gymnast.name] = False
        return context      


def delete_matchup(request, matchup_pk):
    m = get_object_or_404(Matchup, pk=matchup_pk)
    league_pk = m.team1.league.pk
    m.delete()
    return redirect('league_standings', pk=league_pk)

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
    return total

def compute_matchup_winner(request, league_pk, week):
    league = get_object_or_404(League, pk=league_pk)
    matchups = Matchup.objects.filter(week=week, league=league)
    for matchup in matchups:
        team1 = matchup.team1
        team2 = matchup.team2
        team1_lineups = LineUp.objects.filter(team=matchup.team1, week=week)
        team2_lineups = LineUp.objects.filter(team=matchup.team2, week=week)
        team1_score = team_score(team1_lineups)
        team2_score = team_score(team2_lineups)
        if team1_score > team2_score:
            team1.wins += 1
            team2.losses += 1
        elif team2_score > team1_score:
            team2.wins += 1
            team1.losses += 1
        team1.save()
        team2.save()

    return redirect('league_standings', league_pk)