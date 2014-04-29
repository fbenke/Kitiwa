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


def create_recipients_string(combined_transactions):
    recipients = '{'
    for wallet, amount in combined_transactions.items():
        recipients += '"{add}":{amt},'.format(add=wallet, amt=amount)
    return recipients[:-1] + '}'