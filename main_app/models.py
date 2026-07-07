from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

POSITIONS = (
    ('GK', 'Goalkeeper'),
    ('DEF', 'Defender'),
    ('MID', 'Midfielder'),
    ('FWD', 'Forward'),
)

COUNTRIES = (
    ('CA', '🇨🇦 Canada'),
    ('MA', '🇲🇦 Morocco'),
    ('PY', '🇵🇾 Paraguay'),
    ('FR', '🇫🇷 France'),
    ('BR', '🇧🇷 Brazil'),
    ('NO', '🇳🇴 Norway'),
    ('MX', '🇲🇽 Mexico'),
    ('EN', '🏴󠁧󠁢󠁥󠁮󠁧󠁿 England'),
    ('PT', '🇵🇹 Portugal'),
    ('ES', '🇪🇸 Spain'),
    ('US', '🇺🇸 United States'),
    ('BE', '🇧🇪 Belgium'),
    ('AR', '🇦🇷 Argentina'),
    ('EG', '🇪🇬 Egypt'),
    ('CH', '🇨🇭 Switzerland'),
    ('CO', '🇨🇴 Colombia'),
)

API_POSITION_MAP = {
    'Goalkeeper': 'GK',
    'Defender': 'DEF',
    'Midfielder': 'MID',
    'Attacker': 'FWD',
}

FORMATION = (
    ('GK', 'GK'),
    ('LB', 'DEF'),
    ('CB1', 'DEF'),
    ('CB2', 'DEF'),
    ('RB', 'DEF'),
    ('CM1', 'MID'),
    ('CM2', 'MID'),
    ('CM3', 'MID'),
    ('LW', 'FWD'),
    ('ST', 'FWD'),
    ('RW', 'FWD'),
)


class Player(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    position = models.CharField(max_length=3, choices=POSITIONS)
    # API-Football player id; null for rows not sourced from the API
    api_id = models.IntegerField(unique=True, null=True, blank=True)
    # World Cup 2026 tournament stats (snapshot from fetch_players)
    appearances = models.PositiveIntegerField(default=0)
    minutes = models.PositiveIntegerField(default=0)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    rating = models.FloatField(null=True, blank=True)
    shots = models.PositiveIntegerField(default=0)
    shots_on = models.PositiveIntegerField(default=0)
    penalties_scored = models.PositiveIntegerField(default=0)
    penalties_missed = models.PositiveIntegerField(default=0)
    saves = models.PositiveIntegerField(default=0)
    goals_conceded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.get_country_display()} {self.name}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')
    players = models.ManyToManyField(Player, through='TeamPlayer')

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("team-detail", kwargs={"team_id": self.id})


class TeamPlayer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position_in_11 = models.CharField(max_length=3)

    class Meta:
        unique_together = [('team', 'player'), ('team', 'position_in_11')]

    def __str__(self):
        return f"{self.position_in_11}: {self.player.name}"
