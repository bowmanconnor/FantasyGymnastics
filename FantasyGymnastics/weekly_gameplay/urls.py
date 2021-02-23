from django.contrib import admin
from django.urls import path
from core import views as core_views
import weekly_gameplay.views as weekly_views

urlpatterns = [
    path('team/<int:team_pk>/add_gymnast_to_roster/<int:gymnast_pk>/', weekly_views.add_gymnast_to_roster, name = 'add_gymnast_to_roster'),
    path('team/<int:team_pk>/remove_gymnast_to_roster/<int:gymnast_pk>/', weekly_views.remove_gymnast_from_roster, name = 'remove_gymnast_to_roster'),
    path('lineup/<int:lineup_pk>/add_gymnast/<int:gymnast_pk>/', weekly_views.add_gymnast_to_lineup, name='add_gymnast_to_lineup'),
    path('lineup/<int:lineup_pk>/remove_gymnast/<int:gymnast_pk>/', weekly_views.remove_gymnast_from_lineup, name='remove_gymnast_from_lineup'),

    path('league/<int:league_pk>/create_matchup', weekly_views.create_matchup, name='create_matchup'),
    path('delete/matchup/<int:matchup_pk>/', weekly_views.delete_matchup, name='delete_matchup'),
]
