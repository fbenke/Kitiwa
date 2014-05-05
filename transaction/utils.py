def create_recipients_string(combined_transactions):
    recipients = '{'
    for wallet, amount in combined_transactions.items():
        recipients += '"{add}":{amt},'.format(add=wallet, amt=amount)
    return recipients[:-1] + '}'