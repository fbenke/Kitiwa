import requests

from kitiwa.settings import BLOCKCHAIN_TICKER


def get_blockchain_exchange_rate():
    try:
        get_rate = requests.get(BLOCKCHAIN_TICKER)
        if get_rate.status_code == 200:
            try:
                return get_rate.json().get('USD').get('buy')
            except AttributeError:
                return None
        else:
            return None
    except requests.RequestException:
        return None