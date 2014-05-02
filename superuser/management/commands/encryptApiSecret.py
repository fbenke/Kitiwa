import base64
import getpass
import os

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from Crypto.Cipher import AES


class Command(BaseCommand):
    """
    Helper utility to encrypt API_SECRET from Bitstamp with AES-256
    """
    args = 'Iterations (Optional - default: 1000)'
    help = 'Encrypt API_SECRET using a password with AES and pbkdf2_sha256'

    def handle(self, *args, **options):
        """
        Handling the call of the command from the prompt
        :param options: options passed in to the command prompt
        :param args: args passed in to the command prompt
        """

        # Step 1: Get API_SECRET and password from user
        api_secret = getpass.getpass("API Secret (Characters will not be visible): ")
        password = getpass.getpass()

        # Step 2: Key stretching on the password to make it into an acceptable AES key
        try:
            iterations = args[0]
        except IndexError:
            iterations = 1000

        hasher = PBKDF2PasswordHasher()
        salt = get_random_string()
        (algorithm, iterations, salt, key_base64) = hasher.encode(password,
                                                                  salt=salt,
                                                                  iterations=iterations).split('$')

        # Step 3: AES encryption of the API_SECRET using key
        iv = os.urandom(16)
        aes = AES.new(base64.b64decode(key_base64), AES.MODE_CBC, iv)
        enc_api_secret = aes.encrypt(api_secret)

        # Step 4: Show user results
        print 'Salt (Base64):', base64.b64encode(salt).strip()
        print 'IV (Base64):', base64.b64encode(iv).strip()
        print 'Encrypted API Secret (Base64):', base64.b64encode(enc_api_secret).strip()