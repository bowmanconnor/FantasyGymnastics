from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import FantasyTeam, Gymnast, League

@login_required
def index(request, league_pk):
    league = League.objects.filter(pk=league_pk).first()

    context = {}
    context['league_pk'] = league_pk
    context['teams'] = FantasyTeam.objects.filter(league=league_pk)
    context['team'] = FantasyTeam.objects.get(league=league_pk, user=request.user)
    drafted = League.objects.get(pk=league_pk).drafted.all()
    context['gymnasts'] = Gymnast.objects.all().exclude(id__in=drafted)

    if FantasyTeam.objects.filter(user=request.user, league=league_pk).exists() and league.draft_started and not league.draft_complete:
        return render(request, 'draft/draft_test.html', context)
    else:
        return redirect('home')

@login_required
def start_draft(request, league_pk):
    league = League.objects.filter(pk=league_pk).first()

    if league.manager == request.user:
        league.draft_started = True
        league.generate_drafting_order()
        league.save()
        return redirect('/draft/%s' % league_pk)
    else:
        return redirect('/league/%s/standings' % league_pk)