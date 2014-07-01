import hashlib
import re


def create_recipients_string(combined_transactions):
    recipients = '{'
    for wallet, amount in combined_transactions.items():
        recipients += '"{add}":{amt},'.format(add=wallet, amt=amount)
    return recipients[:-1] + '}'


def consolidate_transactions(transactions):
    combined_transactions = {}
    for t in transactions:
        try:
            combined_transactions[t.btc_wallet_address] += t.amount_btc
        except KeyError:
            combined_transactions[t.btc_wallet_address] = t.amount_btc
    return combined_transactions


def consolidate_notification_sms(transactions):
    combined_sms_confirm = {}
    combined_sms_topup = {}
    for t in transactions:
        try:
            combined_sms_confirm[t.notification_phone_number].append(t.reference_number)
        except KeyError:
            combined_sms_confirm[t.notification_phone_number] = [t.reference_number]

        try:
            combined_sms_topup[t.notification_phone_number] += t.amount_ghs
        except (TypeError, KeyError):
            combined_sms_topup[t.notification_phone_number] = t.amount_ghs

    return combined_sms_confirm, combined_sms_topup


def is_valid_btc_address(value):
    value = value.strip()
    if re.match(r"[a-zA-Z1-9]{27,35}$", value) is None:
        return False
    version = get_bcaddress_version(value)
    if version is None:
        return False
    return True


__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)


def b58encode(v):
    """ encode v, which is a string of bytes, to base58.
    """

    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += (256 ** i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    n_pad = 0
    for c in v:
        if c == '\0':
            n_pad += 1
        else:
            break

    return (__b58chars[0] * n_pad) + result


def b58decode(v, length):
    """ decode v into a string of len bytes
    """
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    n_pad = 0
    for c in v:
        if c == __b58chars[0]:
            n_pad += 1
        else:
            break

    result = chr(0) * n_pad + result
    if length is not None and len(result) != length:
        return None

    return result


def b36encode(number, alphabet='0123456789abcdefghijklmnopqrstuvwxyz'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        long_value = 0L
        for (i, c) in enumerate(number[::-1]):
            long_value += (256 ** i) * ord(c)
        number = long_value

    base36 = '' if number != 0 else '0'
    sign = ''
    if number < 0:
        sign = '-'
        number = -number

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def b36decode(number):
    return int(number, 36)


def get_bcaddress_version(str_address):
    """ Returns None if strAddress is invalid. Otherwise returns integer version of address. """
    addr = b58decode(str_address, 25)
    if addr is None:
        return None
    version = addr[0]
    checksum = addr[-4:]
    vh160 = addr[:-4]  # Version plus hash160 is what is check-summed
    h3 = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()
    if h3[0:4] == checksum:
        return ord(version)
    return None


class AcceptException(Exception):
    pass


class PricingException(Exception):
    pass
