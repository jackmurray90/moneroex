from django.shortcuts import render
from django.views import View
from urllib.request import urlopen
from json import loads
from decimal import Decimal
from moneroex.models import Asset, Order, MAX_AMOUNT


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
