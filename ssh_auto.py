#!/usr/bin/python3

import base64
import re
import paramiko


client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


def ssh_automation(user, password, command):

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
        print(error)


command = 'sudo -S ufw status numbered'
password = base64.b64decode("QW1vckZhdGkyMyEk").decode("utf-8")
ssh_response = ssh_automation('rickey', password, command)
if ssh_response:
    print(ssh_response)