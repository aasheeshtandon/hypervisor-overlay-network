from __future__ import print_function
import sys
import libvirt
import sys
import paramiko
import docker
from docker import client

class Connection:
    def __init__(self, secondary_data, tertiary_data, pkey_path='/root/.ssh/id_rsa'):
        try:
            self.secondary_ssh = paramiko.SSHClient()
            privkey = paramiko.RSAKey.from_private_key_file(pkey_path)
            self.secondary_ssh.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.secondary_ssh.connect(
                secondary_data['ip'], username=secondary_data['username'], pkey=privkey)

            self.tertiary_ssh = paramiko.SSHClient()
            privkey = paramiko.RSAKey.from_private_key_file(pkey_path)
            self.tertiary_ssh.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.tertiary_ssh.connect(
                tertiary_data['ip'], username=tertiary_data['username'], pkey=privkey)

            self.primary_conn = libvirt.open('qemu:///system')
            self.secondary_con = libvirt.open(
                'qemu+ssh://{}@{}/system'.format(secondary_data['username'], secondary_data['ip']))
            self.tertiary_con = libvirt.open(
                'qemu+ssh://{}@{}/system'.format(tertiary_data['username'], tertiary_data['ip']))

            self.primary_docker = client.APIClient(
                base_url='unix://var/run/docker.sock')
            self.secondary_docker = client.APIClient(
                base_url="tcp://{}:2375".format(secondary_data['ip']))
            self.tertiary_docker = client.APIClient(
                base_url="tcp://{}:2375".format(tertiary_data['ip']))
        except Exception as e:
            print("Error while initiating connection to remote hypervisor: ", e)
            raise


def ssh_remote(conn, cmd_list):
    res = []
    for cmd in cmd_list:
        ssh_stdin, ssh_stdout, ssh_stderr = conn.exec_command(
            cmd, timeout=300)

        #print(type(ssh_stdout.read())
        
        if ssh_stdout is not '':
            """if ssh_stderr is not None:
                res.append('error:', ssh_stderr.read())
                print(res[-1])
                continue"""
            res.append(ssh_stdout.read())
        print(res[-1])
    return res

"""
conn = libvirt.open('qemu+ssh://ckogant@152.46.18.27/system')


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
privkey = paramiko.RSAKey.from_private_key_file ('/root/.ssh/id_rsa')
ssh.connect('152.46.18.27', username='ckogant', pkey=privkey)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls /tmp')
print(stdout.read())

ns_name='NS1'
cmd = "sudo ip add netns {}; ".format(ns_name)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
print(stdout.read())
"""
