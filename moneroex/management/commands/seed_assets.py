from django.core.management.base import BaseCommand
from moneroex.models import Asset
from decimal import Decimal

# python manage.py seed_assets


class Command(BaseCommand):
    help = "Seed database with assets"

    def handle(self, *args, **kwargs):
        for name, code, decimal_places, transaction_fee in [
            ("Bitcoin", "BTC", 8, Decimal("0.0001")),
            ("Monero", "XMR", 12, Decimal("0.0001")),
        ]:
            try:
                Asset.objects.get(code=code)
            except Asset.DoesNotExist:
                Asset.objects.create(
                    name=name,
                    code=code,
                    decimal_places=decimal_places,
                    transaction_fee=transaction_fee,
                )
