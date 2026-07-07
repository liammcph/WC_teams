from django.core.management.base import BaseCommand
from main_app.models import Player, COUNTRIES

ROSTER = (
    ('GK', 'Goalkeeper', 2),
    ('DEF', 'Defender', 5),
    ('MID', 'Midfielder', 4),
    ('FWD', 'Forward', 4),
)


class Command(BaseCommand):
    help = 'Seeds placeholder players for each country'

    def handle(self, *args, **options):
        Player.objects.all().delete()
        for code, label in COUNTRIES:
            country_name = label.split(' ', 1)[1]
            for position, position_name, count in ROSTER:
                for num in range(1, count + 1):
                    Player.objects.create(
                        name=f'{country_name} {position_name} {num}',
                        country=code,
                        position=position,
                    )
        self.stdout.write(f'Seeded {Player.objects.count()} players')
