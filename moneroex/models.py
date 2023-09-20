from django.db import models


class Asset(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    decimal_places = models.IntegerField()


class Order(models.Model):
    id = models.CharField(max_length=23, primary_key=True)
    payment_asset = models.ForeignKey(
        Asset, related_name="payment_orders", on_delete=models.CASCADE
    )
    payout_asset = models.ForeignKey(
        Asset, related_name="payout_orders", on_delete=models.CASCADE
    )
    payment_amount = models.DecimalField(max_digits=28, decimal_places=18)
    payout_amount = models.DecimalField(max_digits=28, decimal_places=18)
    payment_address = models.CharField(max_length=500, null=True)
    payout_address = models.CharField(max_length=500, null=True)
    expiry = models.DateTimeField()
    complete = models.BooleanField(default=False)
