from django import forms
from django.contrib.auth.models import User
from .models import League

class NewLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        exclude = ['manager']