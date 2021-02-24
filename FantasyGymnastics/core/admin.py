from django.contrib import admin
from .models import Gymnast, Score

# Register your models here.

class GymnastAdmin(admin.ModelAdmin):
    list_display = ('name', 'team')
    list_filter = ('team', 'year')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('gymnast', 'meet', 'event', 'score', 'date', 'week')
    list_filter = ('meet', 'event')

admin.site.register(Gymnast, GymnastAdmin)
admin.site.register(Score, ScoreAdmin)