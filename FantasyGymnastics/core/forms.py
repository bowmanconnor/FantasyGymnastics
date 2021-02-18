from django import forms
from django.contrib.auth.models import User
from .models import League, FantasyTeam, Gymnast

class NewLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        exclude = ['manager', 'requested_to_join', 'drafted']

class NewFantasyTeamForm(forms.ModelForm):
    class Meta:
        model = FantasyTeam
        exclude = ['user', 'gymnasts', 'league']

class NewGymnastForm(forms.ModelForm):
    class Meta:
        model = Gymnast
        fields = '__all__'
