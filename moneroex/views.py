from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from urllib.request import urlopen
from json import loads
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from moneroex.models import Asset, Order, MAX_AMOUNT
from moneroex.util import random_128_bit_string
from datetime import datetime, timezone, timedelta


def get_kraken_ask_bid():
    with urlopen("https://api.kraken.com/0/public/Ticker?pair=XXMRXXBT") as f:
        data = loads(f.read().decode("utf-8"))
    return [Decimal(data["result"]["XXMRXXBT"][i][0]) for i in "ab"]


class IndexView(View):
    def get(self, request):
        ask, bid = get_kraken_ask_bid()
        btc = Asset.objects.get(code="BTC")
        xmr = Asset.objects.get(code="XMR")
        return render(
            request,
            "index.html",
            {
                "ask": ask * Decimal("1.01"),
                "bid": bid * Decimal("0.99"),
                "btc_transaction_fee": btc.transaction_fee,
                "xmr_transaction_fee": xmr.transaction_fee,
            },
        )

    def post(self, request):
        if any(
            any(c not in "0123456789." for c in request.POST[d])
            for d in ["send", "receive"]
        ):
            messages.error(request, "Please enter numbers only")
            return redirect("index")
        try:
            payment = Decimal(request.POST["send"])
            payout = Decimal(request.POST["receive"])
        except InvalidOperation:
            messages.error(request, "Please enter valid numbers only (e.g. 12345.6789)")
            return redirect("index")
        if payment > MAX_AMOUNT or payout > MAX_AMOUNT:
            messages.error(request, f"Please enter less than {MAX_AMOUNT}")
            return redirect("index")
        if payment <= 0 or payout <= 0:
            messages.error(request, "Please enter positive numbers only")
            return redirect("index")
        if request.POST["send_asset"] == "BTC":
            payment_asset = Asset.objects.get(code="BTC")
            payout_asset = Asset.objects.get(code="XMR")
        else:
            payment_asset = Asset.objects.get(code="XMR")
            payout_asset = Asset.objects.get(code="BTC")
        if -payment.as_tuple().exponent > payment_asset.decimal_places:
            messages.error(
                request,
                f"Please enter a maximum of {payment_asset.decimal_places} decimal places for {payment_asset.name}",
            )
            return redirect("index")
        if -payout.as_tuple().exponent > payout_asset.decimal_places:
            messages.error(
                request,
                f"Please enter a maximum of {payout_asset.decimal_places} decimal places for {payout_asset.name}",
            )
            return redirect("index")
        ask, bid = get_kraken_ask_bid()
        ask = ask * Decimal("1.0075")
        bid = bid * Decimal("0.9925")
        if request.POST["send_asset"] == "BTC":
            if payment / (payout + payout_asset.transaction_fee) < ask:
                messages.error(request, "Offer expired, please try again")
                return redirect("index")
        else:
            if (payout + payout_asset.transaction_fee) / payment > bid:
                messages.error(request, "Offer expired, please try again")
                return redirect("index")
        maximum_payout_amount = (
            payout_asset.exchange_balance - payout_asset.transaction_fee
        )
        if payout > maximum_payout_amount:
            messages.error(
                request,
                f"Not enough funds on exchange to complete order, maximum payout amount is {maximum_payout_amount} {payout_asset.code}",
            )
            return redirect("index")

        # At this point we have verified payment for payout is something that
        # is profitable for us and we can satisfy the order
        # So we subtract the payout amount from the exchange balance and create
        # the order for the customer.
        payout_asset.exchange_balance -= payout + payout_asset.transaction_fee
        payout_asset.save()

        order = Order.objects.create(
            id=random_128_bit_string(),
            payment_asset=payment_asset,
            payout_asset=payout_asset,
            payment_amount=payment,
            payout_amount=payout,
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        return redirect("order", id=order.id)


class OrderView(View):
    def get(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            raise Http404
        return render(request, "order.html", {"order": order})
