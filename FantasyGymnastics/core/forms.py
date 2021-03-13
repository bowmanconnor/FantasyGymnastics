from django import forms
from django.contrib.auth.models import User
from .models import League, FantasyTeam, Gymnast, Score, ContactUs

class NewLeagueForm(forms.ModelForm):
    class Meta:
        model = League
        exclude = ['manager', 'requested_to_join', 'drafted', 'currently_drafting', 'draft_started', 'draft_complete']
        help_texts = {
            'name': 'League name must be unique',
            'roster_size': 'Our recommendation: 17 man roster',
            'lineup_size': 'Our recommendation: 15 man competition roster',
            'event_lineup_size': 'Our recommendation: 5 up',
            'event_count_size': 'Our recommendation: 3 count',
        }
        error_messages = {
            'name': {
                'unique' : 'A league with that name already exists. Check MyLeagues to ensure you didn\'t double sumbit this league name.',
            }
        }

class NewFantasyTeamForm(forms.ModelForm):
    class Meta:
        model = FantasyTeam
        exclude = ['user', 'roster', 'league', 'wins', 'losses', 'draft_position', 'currently_in_draft']

class NewGymnastForm(forms.ModelForm):
    class Meta:
        model = Gymnast
        fields = '__all__'

class NewScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = '__all__'

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['message',]