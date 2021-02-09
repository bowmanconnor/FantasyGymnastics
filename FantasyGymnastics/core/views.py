from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import League, FantasyTeam
from django.views.generic import UpdateView, DetailView, ListView

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
            return redirect('home')
    else:
        form = NewLeagueForm()
    return render(request, 'core/create_league.html', {'form': form})

class LeagueDetailView(DetailView):
    model = League
    template_name = 'core/view_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = FantasyTeam.objects.filter(league_id=context['object'].id)
        return context

# @method_decorator(staff_member_required(login_url='home') , name='dispatch')
class LeagueUpdateView(UpdateView):
    model = League
    form_class = NewLeagueForm

    template_name = 'core/edit_league.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'league'

    def form_valid(self, form):
        league = form.save(commit=False)
        league.save()
        return redirect('view_league', pk=league.pk)

class LeagueSearchResultsView(ListView):
    model = League
    template_name = 'core/league_search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        query = self.request.GET.get('query')
        context['leagues'] = League.objects.filter(name__icontains=query)
        return context

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

class FantasyTeamUpdateView(UpdateView):
    model = FantasyTeam
    form_class = NewFantasyTeamForm

    template_name = 'core/edit_team.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'team'

    def form_valid(self, form):
        team = form.save(commit=False)
        team.save()
        return redirect('view_team', pk=team.pk)

def home(request):
    context = {}
    context['leagues'] = League.objects.all()
    return render(request, 'core/home.html', context)

