# main_app/views.py

from django.shortcuts import render, redirect
from .models import Team, Player, COUNTRIES, FORMATION
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class Home(LoginView):
    # this class sends a auth form to this home template
    template_name = 'home.html'


def signup(request):
    # this we will populate with a error message if we have one
    error_message = ''
    # Check if we are in a post request and handle the form
    if request.method == "POST":
        # request.POST === req.body
        form = UserCreationForm(request.POST) # makes a instance of the form including the fields the user filled out

        if form.is_valid():
            user = form.save() # Saves user to the db
            login(request, user) # automagically log in this user
            return redirect('team-index')

        else:
            error_message = 'Invalid sign up - try again'

    form = UserCreationForm()
    return render(request, 'signup.html', {
        'form': form,
        'error_message': error_message
    })


def about(request):
    # Send a simple HTML response
    return render(request, 'about.html')


@login_required # this makes this a protected route
def team_index(request):
    # INDEX
    # go in the db get all this user's teams
    teams = request.user.teams.all() # ORM Object Relational Mapper
    return render(request, 'teams/index.html', { 'teams': teams })


@login_required
def team_detail(request, team_id):
    # get back a team
    team = Team.objects.get(id=team_id)

    selected_country = request.GET.get('country', COUNTRIES[0][0])

    # Fetch players from that country but skip ones already on the team
    players = Player.objects.filter(country=selected_country).exclude(
        id__in=team.players.all().values_list('id'))

    lineup = []
    for slot, position in FORMATION:
        team_player = team.team_players.filter(position_in_11=slot).first()
        lineup.append({
            'slot': slot,
            'position': position,
            'player': team_player.player if team_player else None,
        })

    return render(request, 'teams/detail.html', {
        'team': team,
        'players': players,
        'lineup': lineup,
        'countries': COUNTRIES,
        'selected_country': selected_country,
    })


@login_required
def add_player(request, team_id, player_id):
    team = Team.objects.get(id=team_id)
    player = Player.objects.get(id=player_id)
    taken = team.team_players.values_list('position_in_11', flat=True)
    for slot, position in FORMATION:
        if position == player.position and slot not in taken:
            team.players.add(player, through_defaults={'position_in_11': slot})
            break
    return redirect('team-detail', team_id=team_id)


@login_required
def remove_player(request, team_id, player_id):
    Team.objects.get(id=team_id).players.remove(player_id)
    return redirect('team-detail', team_id=team_id)


# CreateView handles both the GET and POST request
#   It also handles creating a form using Django's ModelForm
class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['name']

    # override the CreateView default check if a form is valid
    def form_valid(self, form):
        # add a user into the current form
        # similar req.body.user = req.session.user
        form.instance.user = self.request.user
        return super().form_valid(form) # Eventually saves the team to the db


class TeamUpdate(LoginRequiredMixin, UpdateView):
    model = Team
    fields = ['name']


class TeamDelete(LoginRequiredMixin, DeleteView):
    model = Team
    success_url = '/teams/'
