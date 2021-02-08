from django.contrib import admin
from django.urls import path
from core import views as views
urlpatterns = [
    path('create_league/', views.create_league, name="create_league"),
    path('', views.home, name="home"),
    path('view/<int:pk>/', views.view_league_detail.as_view(), name="view_league")
]
