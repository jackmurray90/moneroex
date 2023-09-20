from django.shortcuts import render
from django.views import View
from urllib.request import urlopen
from json import loads
from decimal import Decimal


class IndexView(View):
    def get(self, request):
        with urlopen("https://api.kraken.com/0/public/Ticker?pair=XXMRXXBT") as f:
            data = loads(f.read().decode("utf-8"))
        ask, bid = [Decimal(data["result"]["XXMRXXBT"][i][0]) for i in "ab"]
        return render(
            request,
            "index.html",
            {"ask": ask * Decimal("1.01"), "bid": bid * Decimal("0.99")},
        )
