#!/usr/bin/python3

import os
import stat
from getpass import getpass
from cryptography.fernet import Fernet


def check_password(password1, password2):

    # Initiat count for attempts (max 3)
    count = 0

    # Verify password meets standards
    # Password must be greater than 10 characters
    while (
        password1 != password2 or
        len(password1) < 10
    ):
        while (password1 != password2):
            print('\nPasswords do not match.')
            password1 = getpass('Password: ')
            password2 = getpass('Confirm password: ')
            count += 1
            if (count > 2):
                print('\nPasswords do not match.')
                exit()
        while (len(password1) < 10):
            print('\nPassowrd must be 10 characters or more.')
            password1 = getpass('Password: ')
            password2 = getpass('Confirm password: ')
            count += 1
            if (count > 2):
                print('\nPassowrd must be 10 characters or more.')
                exit()

    return password1


def gen_key_token(password1):

    # Define file name directory to store key and token
    SECRETS_DIR = os.path.join(os.path.expanduser('~'), '.secrets/')
    SECRET_KEY = 'secret.key'
    TOKEN = 'token.pub'

    # generate secret key and token
    key = Fernet.generate_key().decode('utf-8')
    cipher = Fernet(key)
    password = password1.encode('utf-8')
    token = cipher.encrypt(password).decode('utf-8')

    # Create directory if it does not exist
    if not os.path.exists(SECRETS_DIR):
        os.mkdir(SECRETS_DIR)
    os.chmod(SECRETS_DIR, stat.S_IRWXU)

    # Write key and token to secrets file
    secrets_key_fn = os.path.join(SECRETS_DIR, SECRET_KEY)
    with open(secrets_key_fn, 'w') as f:
        f.write(f'key={key}\n')
    os.chmod(secrets_key_fn, stat.S_IRUSR | stat.S_IWUSR)

    token_fn = os.path.join(SECRETS_DIR, TOKEN)
    with open(token_fn, 'w') as f:
        f.write(f'token={token}')
    os.chmod(
        token_fn, 
        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    )
    # cipher = Fernet(key)
    # uncoded_password = cipher.decrypt(token).decode('utf-8')


def gen_secrets():
    print('Please enter a passowrd, must be 10 characters or more.')
    password1 = getpass('Password: ')
    password2 = getpass('Confirm password: ')

    check_password(password1, password2)
    gen_key_token(password1)


if __name__ == '__main__':
    gen_secrets()
