from django.contrib import admin
from django.urls import path
from core import views as views
urlpatterns = [
    path('', views.home, name="home"),

    path('how_to_play/', views.how_to_play, name="how_to_play"),

    path('league/create/', views.create_league, name="create_league"),
    path('league/edit/<int:pk>/', views.UpdateLeague.as_view(), name="edit_league"),
    path('myleagues/', views.myleagues, name='myleagues'),

    path('league/create/', views.create_league, name="create_league"),
    path('league/<int:pk>/edit/', views.UpdateLeague.as_view(), name="edit_league"),
    path('league/<int:pk>/standings/', views.LeagueStandings.as_view(), name="league_standings"),
    path('league/search/', views.SearchLeagues.as_view(), name='league_search'),
    path('league/<int:pk>/request_to_join/', views.request_to_join_league, name="request_to_join_league"),
    path('league/<int:league_pk>/approve_user/<int:user_pk>/', views.approve_player_into_league, name="approve_player_into_league"),
    path('league/<int:league_pk>/reject_user/<int:user_pk>/', views.reject_player_from_league, name="reject_player_from_league"),
    path('league/<int:league_pk>/remove_team/<int:team_pk>/', views.remove_team_from_league, name="remove_team_from_league"),
    path('league/<int:pk>/delete/', views.delete_league, name='delete_league'),

    path('team/view/<int:pk>/', views.ViewFantasyTeam.as_view(), name="view_team"),
    path('team/edit/<int:pk>/', views.UpdateFantasyTeam.as_view(), name="edit_team"),
    path('team/<int:pk>/gymnast/search/', views.SearchGymnasts.as_view(), name='gymnast_search'),

    path('gymnast/<int:gymnast_pk>/view/', views.view_gymnast, name='view_gymnast'),

    path('cutter/', views.cutter, name='cutter'),
]