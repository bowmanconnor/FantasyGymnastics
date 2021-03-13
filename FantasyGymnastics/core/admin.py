from django.contrib import admin
from .models import Gymnast, Score, League, FantasyTeam

# Register your models here.

class GymnastAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    list_filter = ('team', 'year')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('gymnast', 'meet', 'event', 'score', 'date', 'week')
    list_filter = ('meet', 'event')

class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'draft_started', 'draft_complete')

class FantasyTeamAdmin(admin.ModelAdmin):
    list_display = ('league', 'name')

admin.site.register(Gymnast, GymnastAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(League, LeagueAdmin)
admin.site.register(FantasyTeam, FantasyTeamAdmin)
