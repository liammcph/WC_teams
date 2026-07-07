import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from main_app.models import Player

DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'world_cup_2026_players.json'


class Command(BaseCommand):
    help = f'Seeds players from {DATA_PATH.name} (generate it with `manage.py fetch_players`)'

    def handle(self, *args, **options):
        if not DATA_PATH.exists():
            raise CommandError(f'{DATA_PATH} not found — run `manage.py fetch_players` first')
        with open(DATA_PATH) as f:
            data = json.load(f)

        players = data['players']
        ids = [p['api_id'] for p in players]
        created_count = 0
        with transaction.atomic():
            # Placeholder players have no api_id; removing them cascades to
            # TeamPlayer, clearing any lineup slots that used them
            _, detail = Player.objects.filter(api_id__isnull=True).delete()
            placeholders = detail.get('main_app.Player', 0)
            # Separate query: exclude(api_id__in=ids) never matches NULL api_id rows
            _, detail = Player.objects.filter(api_id__isnull=False).exclude(api_id__in=ids).delete()
            stale = detail.get('main_app.Player', 0)
            for fields in players:
                _, created = Player.objects.update_or_create(
                    api_id=fields['api_id'],
                    defaults={k: v for k, v in fields.items() if k != 'api_id'},
                )
                created_count += created

        self.stdout.write(self.style.SUCCESS(
            f'Created {created_count}, updated {len(players) - created_count}, '
            f'removed {placeholders} placeholder and {stale} stale players '
            f'(data fetched {data["fetched_at"]})'
        ))
