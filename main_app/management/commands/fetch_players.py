import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from django.core.management.base import BaseCommand, CommandError

from main_app.models import API_POSITION_MAP, COUNTRIES

BASE_URL = 'https://v3.football.api-sports.io'
LEAGUE_ID = 1  # FIFA World Cup
SEASON = 2026
SLEEP_SECONDS = 7  # free-tier rate limit is 10 requests/minute
DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'world_cup_2026_players.json'

# COUNTRIES labels look like "🇫🇷 France" — map plain name back to our 2-char code
NAME_TO_CODE = {label.split(' ', 1)[1]: code for code, label in COUNTRIES}
# API team names that differ from our COUNTRIES labels
API_NAME_ALIASES = {
    'USA': 'US',
    'United States': 'US',
}


class Command(BaseCommand):
    help = f'Fetches World Cup {SEASON} squads and stats from API-Football into {DATA_PATH.name}'

    def handle(self, *args, **options):
        api_key = os.environ.get('API_FOOTBALL_KEY', '')
        if not api_key or api_key == 'paste-your-key-here':
            raise CommandError(
                'API_FOOTBALL_KEY is not set. Put it in .env (loaded automatically '
                'by `pipenv run` / `pipenv shell`) or export it in your shell.'
            )
        self.session = requests.Session()
        self.session.headers['x-apisports-key'] = api_key

        team_ids = self.fetch_team_ids()
        players = {}
        for code, team_id in team_ids.items():
            squad = self.fetch_team_players(code, team_id)
            players.update(squad)
            self.stdout.write(f'{code}: {len(squad)} players')

        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_PATH, 'w') as f:
            json.dump({
                'fetched_at': datetime.now(timezone.utc).isoformat(),
                'league': LEAGUE_ID,
                'season': SEASON,
                'players': sorted(players.values(), key=lambda p: (p['country'], p['name'])),
            }, f, indent=2, ensure_ascii=False)
        self.stdout.write(self.style.SUCCESS(f'Wrote {len(players)} players to {DATA_PATH}'))

    def get(self, path, params):
        resp = self.session.get(f'{BASE_URL}{path}', params=params, timeout=30)
        if resp.status_code != 200:
            raise CommandError(f'{path} returned HTTP {resp.status_code}: {resp.text[:300]}')
        body = resp.json()
        # The API reports plan/parameter problems inside a 200 body
        if body.get('errors'):
            raise CommandError(f'API error on {path}: {body["errors"]}')
        time.sleep(SLEEP_SECONDS)
        return body

    def fetch_team_ids(self):
        body = self.get('/teams', {'league': LEAGUE_ID, 'season': SEASON})
        team_ids = {}
        for item in body['response']:
            name = item['team']['name']
            code = NAME_TO_CODE.get(name) or API_NAME_ALIASES.get(name)
            if code:
                team_ids[code] = item['team']['id']
        missing = set(NAME_TO_CODE.values()) - set(team_ids)
        if missing:
            api_names = sorted(item['team']['name'] for item in body['response'])
            raise CommandError(
                f'No API team matched for: {sorted(missing)}. '
                f'Add aliases to API_NAME_ALIASES. API team names: {api_names}'
            )
        return team_ids

    def fetch_team_players(self, code, team_id):
        squad = {}
        page, total_pages = 1, 1
        while page <= total_pages:
            body = self.get('/players', {
                'league': LEAGUE_ID, 'season': SEASON, 'team': team_id, 'page': page,
            })
            total_pages = body['paging']['total']
            page += 1
            for item in body['response']:
                player = self.trim_player(item, code)
                if player:
                    squad[player['api_id']] = player
        return squad

    def trim_player(self, item, code):
        stats = next(
            (s for s in item['statistics'] if s.get('league', {}).get('id') == LEAGUE_ID),
            None,
        )
        if stats is None:
            return None
        games, goals = stats['games'], stats['goals']
        position = API_POSITION_MAP.get(games.get('position'))
        if position is None:
            self.stderr.write(
                f"Skipping {item['player']['name']} ({code}): "
                f"unmapped position {games.get('position')!r}"
            )
            return None
        rating = games.get('rating')
        return {
            'api_id': item['player']['id'],
            'name': item['player']['name'][:100],
            'country': code,
            'position': position,
            'appearances': _i(games.get('appearences')),  # sic: API misspells it
            'minutes': _i(games.get('minutes')),
            'goals': _i(goals.get('total')),
            'assists': _i(goals.get('assists')),
            'rating': round(float(rating), 2) if rating else None,
            'shots': _i(stats['shots'].get('total')),
            'shots_on': _i(stats['shots'].get('on')),
            'penalties_scored': _i(stats['penalty'].get('scored')),
            'penalties_missed': _i(stats['penalty'].get('missed')),
            'saves': _i(goals.get('saves')),
            'goals_conceded': _i(goals.get('conceded')),
        }


def _i(value):
    return int(value) if value is not None else 0
