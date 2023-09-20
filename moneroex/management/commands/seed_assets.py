from django.core.management.base import BaseCommand
from moneroex.models import Asset

# python manage.py seed_assets


class Command(BaseCommand):
    help = "Seed database with assets"

    def handle(self, *args, **kwargs):
        for name, code, decimal_places in [
            ("Bitcoin", "BTC", 8),
            ("Monero", "XMR", 12),
        ]:
            try:
                Asset.objects.get(code=code)
            except Asset.DoesNotExist:
                Asset.objects.create(
                    name=name, code=code, decimal_places=decimal_places
                )
