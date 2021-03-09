from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import FantasyTeam

@login_required
def index(request, league_pk):
    context = {}
    context['league_pk'] = league_pk
    context['teams'] = FantasyTeam.objects.filter(league=league_pk)
    if FantasyTeam.objects.filter(user=request.user, league=league_pk).exists():
        return render(request, 'draft/draft_test.html', context)
    else:
        return redirect('home')