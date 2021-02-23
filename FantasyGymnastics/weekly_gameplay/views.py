from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.models import League, FantasyTeam, Gymnast, LineUp
from django.views.generic import UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import NewMatchupForm
from .models import Matchup
# Create your views here.

def add_gymnast_to_roster(request, team_pk, gymnast_pk):
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    team = get_object_or_404(FantasyTeam, pk=team_pk)
    team.roster.add(gymnast)
    league = team.league
    league.drafted.add(gymnast)
    return redirect('view_team', pk=team_pk)

def remove_gymnast_from_roster(request, team_pk, gymnast_pk):
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    team = get_object_or_404(FantasyTeam, pk=team_pk)
    team.roster.remove(gymnast)
    league = team.league
    league.drafted.remove(gymnast)
    return redirect('view_team', pk=team_pk)

def add_gymnast_to_lineup(request, lineup_pk, gymnast_pk):
    lineup = get_object_or_404(LineUp, pk=lineup_pk)
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    lineup.gymnasts.add(gymnast)
    return(redirect('view_team', pk=lineup.team.pk))

def remove_gymnast_from_lineup(request, lineup_pk, gymnast_pk):
    lineup = get_object_or_404(LineUp, pk=lineup_pk)
    gymnast = get_object_or_404(Gymnast, pk=gymnast_pk)
    lineup.gymnasts.remove(gymnast)
    return(redirect('view_team', pk=lineup.team.pk))


@login_required
def create_matchup(request, league_pk):
    if request.method == 'POST':
        form = NewMatchupForm(request.POST)
        if form.is_valid():
            matchup = form.save(commit=False)
            if Matchup.objects.filter(team1=matchup.team1, week=matchup.week).exists() or Matchup.objects.filter(team2=matchup.team2, week=matchup.week).exists() or Matchup.objects.filter(team1=matchup.team2, week=matchup.week).exists() or Matchup.objects.filter(team2=matchup.team1, week=matchup.week).exists() or matchup.team1 == matchup.team2:
                print("DUPLICATE")
            else:
                matchup.save()
            return redirect('league_standings', pk=league_pk)
    else:
        form = NewMatchupForm()
    return render(request, 'weekly_gameplay/create_matchup.html', {'form': form})

def delete_matchup(request, matchup_pk):
    m = get_object_or_404(Matchup, pk=matchup_pk)
    league_pk = m.team1.league.pk
    m.delete()
    return redirect('league_standings', pk=league_pk)
