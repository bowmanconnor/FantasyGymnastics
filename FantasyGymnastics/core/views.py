from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import League, FantasyTeam
from django.views.generic import UpdateView, DetailView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin


from .forms import NewLeagueForm, NewFantasyTeamForm
# Create your views here.

@login_required
def create_league(request):
    if request.method == 'POST':
        form = NewLeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            league.manager = request.user
            league.save()
            team = FantasyTeam.objects.create(
                user=request.user,
                league=league,
                name=str(request.user)+"'s Team")
            return redirect('home')
    else:
        form = NewLeagueForm()
    return render(request, 'core/create_league.html', {'form': form})

def view_leagues(request):
    context = {}
    context['leagues'] = League.objects.all()
    return render(request, 'core/view_leagues.html', context)

@login_required
def request_to_join_league(request, pk):
    league = get_object_or_404(League, pk=pk)
    team = FantasyTeam.objects.filter(
        user=request.user,
        league=league
    )
    if len(team) == 0:
        if request.user not in league.requested_to_join.all():
            league.requested_to_join.add(request.user)
    return redirect('view_league', pk=league.pk)


def approve_player_into_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        user = get_object_or_404(User, pk=user_pk)
        team = FantasyTeam.objects.create(
            user=user,
            league=league,
            name=str(user.first_name)+"'s Team")
        team.save()
        league.requested_to_join.remove(user)
    return redirect('view_league', pk=league.pk)

def reject_player_from_league(request, league_pk, user_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        user = get_object_or_404(User, pk=user_pk)
        league.requested_to_join.remove(user)
    return redirect('view_league', pk=league.pk)

def remove_team_from_league(request, league_pk, team_pk):
    league = get_object_or_404(League, pk=league_pk)
    if request.user == league.manager:
        get_object_or_404(FantasyTeam, pk=team_pk).delete()
    return redirect('view_league', pk=league_pk)

class LeagueDetailView(DetailView):
    model = League
    template_name = 'core/view_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = FantasyTeam.objects.filter(league_id=context['object'].id)
        context['requested_to_join'] = context['object'].requested_to_join
        print(context['teams'])
        return context

class LeagueUpdateView(UserPassesTestMixin, UpdateView):
    model = League
    form_class = NewLeagueForm

    template_name = 'core/edit_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.manager

    def form_valid(self, form):
        league = form.save(commit=False)
        league.save()
        return redirect('view_league', pk=league.pk)

@login_required
def create_team(request, pk):
    if request.method == 'POST':
        form = NewFantasyTeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.user = request.user
            team.league = League.objects.get(pk=pk)
            team.save()
            return redirect('home')
    else:
        form = NewFantasyTeamForm()
    return render(request, 'core/create_team.html', {'form': form})
 
class FantasyTeamDetailView(DetailView):
    model = FantasyTeam
    template_name = 'core/view_team.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context      

class FantasyTeamUpdateView(UserPassesTestMixin, UpdateView):
    model = FantasyTeam
    form_class = NewFantasyTeamForm
    template_name = 'core/edit_team.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user

    def form_valid(self, form):
        team = form.save(commit=False)
        team.save()
        return redirect('view_team', pk=team.pk)


def home(request):
    return render(request, 'core/home.html')

