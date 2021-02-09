from django.contrib import admin
from django.urls import path
from core import views as views
urlpatterns = [
    path('', views.home, name="home"),
    path('league/create/', views.create_league, name="create_league"),
    path('league/view/<int:pk>/', views.LeagueDetailView.as_view(), name="view_league"),
    path('league/edit/<int:pk>/', views.LeagueUpdateView.as_view(), name="edit_league"),
    path('league/<int:pk>/team/create/', views.create_team, name="create_team"),
    path('team/view/<int:pk>/', views.FantasyTeamDetailView.as_view(), name="view_team"),
    path('team/edit/<int:pk>/', views.FantasyTeamUpdateView.as_view(), name="edit_team"),

]
