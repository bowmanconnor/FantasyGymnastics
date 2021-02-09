from django import forms
from django.contrib.auth.models import User
from .models import League, FantasyTeam

class NewLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        exclude = ['manager']

class NewFantasyTeamForm(forms.ModelForm):
    class Meta:
        model = FantasyTeam
        exclude = ['user', 'gymnasts', 'league']