from django.contrib import admin
from django.urls import path
from draft import views as views

urlpatterns = [
    path('draft/<int:league_pk>/', views.index, name="index"),
    path('draft/start/<int:league_pk>', views.start_draft, name="start_draft")
]