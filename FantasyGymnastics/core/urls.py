from django.contrib import admin
from django.urls import path
from core import views as views
urlpatterns = [
    path('', views.home, name="home"),

    path('myleagues/', views.myleagues, name='myleagues'),
    path('league/create/', views.create_league, name="create_league"),
    path('league/search/', views.LeagueSearchResultsView.as_view(), name='league_search'),


    path('league/<int:pk>/request_to_join/', views.request_to_join_league, name="request_to_join_league"),
    path('league/<int:league_pk>/approve/<int:user_pk>', views.approve_player_into_league, name="approve_player_into_league"),
    path('league/<int:league_pk>/reject/<int:user_pk>', views.reject_player_from_league, name="reject_player_from_league"),
    path('league/<int:league_pk>/remove_team/<int:team_pk>', views.remove_team_from_league, name="remove_team_from_league"),
    path('league/view/<int:pk>/', views.LeagueDetailView.as_view(), name="view_league"),
    path('league/edit/<int:pk>/', views.LeagueUpdateView.as_view(), name="edit_league"),

    path('team/view/<int:pk>/', views.FantasyTeamDetailView.as_view(), name="view_team"),
    path('team/edit/<int:pk>/', views.FantasyTeamUpdateView.as_view(), name="edit_team"),


    path('delete_gymnast/<int:pk>', views.delete_gymnast, name='delete_gymnast'),
]

