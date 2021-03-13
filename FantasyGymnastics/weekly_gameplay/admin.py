from django.contrib import admin
from weekly_gameplay.models import Matchup

# Register your models here.

class MatchupAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'league', 'week')
    list_filter = ('league', 'week')

admin.site.register(Matchup, MatchupAdmin)