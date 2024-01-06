#!/usr/bin/python3

import os
import re
import shutil
import paramiko
from cryptography.fernet import Fernet

import secret_token


SECRETS_DIR = os.path.join(os.path.expanduser('~'), '.secrets/')
SECRET_KEY = 'secret.key'
TOKEN = 'token.pub'


def rm_bad_keys():

    if os.path.exists(SECRETS_DIR):
        shutil.rmtree(SECRETS_DIR)


def ssh_automation(user, password, command):

    client = paramiko.SSHClient()

    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            'eros',
            username=user,
            password=password,
        )

        # Run a command
        stdin, stdout, stderr = client.exec_command(command)

        if re.match('^sudo -S.+', command):
            stdin.write(password)
            stdin.channel.shutdown_write()

        if stderr.channel.recv_exit_status() != 0:
            print(f'\nError: {stderr.read().decode("utf-8")}')
            client.close()
            return None

        else:
            response = stdout.read().decode("utf-8")
            client.close()

            return response

    except Exception as error:
        if re.search(r'Bad authentication', error.args[0]):
            rm_bad_keys()
        print(error)


def get_pass_hash():

    if not os.path.exists(os.path.join(SECRETS_DIR, SECRET_KEY)):
        secret_token.gen_keys()

    if (
        os.path.exists(os.path.join(SECRETS_DIR, SECRET_KEY)) and
        os.path.exists(os.path.join(SECRETS_DIR, TOKEN))
    ):
        key_fn = os.path.join(SECRETS_DIR, SECRET_KEY)

        with open(key_fn, 'r') as f:
            key = re.search(r'^key=(.+)', f.read())[1]

        token_fn = os.path.join(SECRETS_DIR, TOKEN)
        with open(token_fn, 'r') as f:
            token = re.search(r'^token=(.+)', f.read())[1]

        cipher = Fernet(key)
        uncoded_password = cipher.decrypt(token).decode('utf-8')

        return uncoded_password


def main():

    command = 'sudo -S ufw status numbered'
    get_pass_hash()
    ssh_response = ssh_automation('rickey', get_pass_hash(), command)
    if ssh_response:
        print(ssh_response)


if __name__ == '__main__':
    main()
