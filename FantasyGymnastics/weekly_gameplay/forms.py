from django import forms
from django.contrib.auth.models import User
from .models import Matchup

class NewMatchupForm(forms.ModelForm):
    class Meta:
        model = Matchup
        exclude = ['league']

