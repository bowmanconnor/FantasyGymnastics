from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from core.models import League, FantasyTeam, Gymnast
from django.views.generic import UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
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