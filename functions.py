from __future__ import print_function

import os
import signal
import commands
from time import sleep

import docker
import tenant_management
from connection import Connection
from connection import ssh_remote
from docker import client


class TimedOutExc(Exception):
      pass

def deadline(timeout, *args):
  def decorate(f):
    def handler(signum, frame):
      pass
 
    def new_f(*args):
      
      signal.signal(signal.SIGALRM, handler)
      signal.alarm(timeout)
      return f(*args)

    new_f.__name__ = f.__name__
    return new_f
  return decorate

print("fucntions imported")

prefix = 'sudo ip netns exec '

"""@deadline(60)
def create_vm(vm_name, memory,bridge_name,iso_path,primary):
    cmd = "sudo virt-install --name {} --memory {} " \
        "--vcpu=1 --cpu host  --disk path=/var/lib/libvirt/images/{}.img,size=8" \
        " --network network={} -c {} -v".format(
            vm_name, memory, vm_name, bridge_name, iso_path)
    print(cmd)
    try:
        if primary == True:
            print('local:')
            os.system(cmd)
            return
        ssh_remote(conn, [cmd])
    except Exception as e:
        print("timeout in create_vm {}".format(e))
        pass
    return"""


def create_docker_container(c_name, veth1, c_cidr, gw,  conn, ssh_conn=None, primary=True):
    """
    Creates a Docker Container, veth pair, assigns IP and moves veth1 to container
    :param c_name: Name for the container
    :param veth0: Name for the veth interface which stays in the bridge/hypervisor
    :param veth1: Name for the veth interface which goes into the docker container
    :param c_cidr: X.X.X.X/24 for veth1 (docker veth Interface)
    :param conn:
    :param primary:
    :return: container_id
    """
    
    host_c = conn.create_host_config(privileged=True)
    c_id = conn.create_container(image='atandon70/ubuntu_project:loadedUBUNTUimage',
                                command='/bin/sleep 3000000',
                                host_config=host_c,
                                name=c_name)
    container_id = c_id['Id']
    conn.start(container_id)
    c_pid = conn.inspect_container(c_id['Id'])['State']['Pid']
    cmd1 = "sudo ip link set {0} netns {1}".format(veth1, c_pid)
    cmd2 = "sudo docker exec -i --privileged {0} ip addr add {1} dev {2} ".format(
        c_id['Id'], c_cidr, veth1)
    cmd3 = "sudo docker exec -i --privileged {0} ip link set {1} up ".format(
        c_id['Id'], veth1)
    cmd4 = "sudo docker exec -i --privileged {0} ip route del default".format(c_id['Id'])
    cmd5 = "sudo docker exec -i --privileged {0} ip route add default via {1}".format(
        c_id['Id'], gw)
    cmd_list = [cmd1, cmd2, cmd3, cmd4, cmd5]

    if primary==True:
        print('local:')
        for cmd in cmd_list:
            print(cmd)
            os.system(cmd)
        return container_id
    print(cmd_list)
    ssh_remote(ssh_conn, cmd_list)
    return container_id

def get_mac_dockerContainer(container_id, conn=None, primary=True):
    """
    This parses the veth1 in the container for its MAC address
    :param container_id: Container ID for which veth1's MAC is required
    :param conn:
    :param primary:
    :return: returns the MAC address of the container veth1 interface
    """
    cmd = "sudo docker exec -i %s ifconfig -a| grep -A2 --no-group-separator 'Y'| grep HWaddr | awk '{print $5}'" % container_id
    print(cmd)
    if primary == True:
        print('local:')
        status, c_mac = commands.getstatusoutput(cmd)
        return c_mac
    data = ssh_remote(conn, [cmd])
    c_mac = data[0].split('\n')[0]
    return c_mac

def create_namespace(name, conn=None, primary=True):
    cmd = 'sudo ip netns add {}'.format(name)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd) 
        return
    ssh_remote(conn, [cmd])
    return

def create_vethpair(name1, name2, conn=None, primary=True):
    cmd = 'sudo ip link add {} type veth peer name {}'.format(name1, name2)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return

def set_link_up(interface_name, conn=None, primary=True):
    cmd= 'sudo ip link set dev {} up'.format(interface_name)
    print(cmd)
    if primary == True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def set_link_up_in_namespace(name_space, interface, conn=None, primary=True):
    global prefix
    cmd= prefix + name_space + ' ip link set dev {} up'.format(interface)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def assign_ip_address_namespace(name_space, interface, ip_address, conn=None, primary=True):
    global prefix
    cmd = prefix + name_space + ' ip addr add '+ ip_address + ' dev {}'.format(interface)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def assign_ip_address(interface, ip_address, conn=None, primary=True):
    cmd = 'sudo ip addr add {} dev {}'.format(ip_address,interface)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def move_veth_to_namespace(vethname, name_space, conn=None, primary=True):
    cmd = 'sudo ip link set {} netns {}'.format(vethname, name_space)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def move_veth_to_bridge(vethname, bridge_name, conn=None, primary=True):
    cmd = 'sudo brctl addif {} {}'.format(bridge_name, vethname)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def move_veth_to_bridge_namespace(name_space, vethname, bridge_name, conn=None, primary=True):
    global prefix
    cmd = prefix+ '{} sudo brctl addif {} {}'.format(name_space, bridge_name, vethname)
    print(cmd)
    if primary == True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def create_gre_tunnel_namespace(name_space, remote_ip, local_ip, gre_tunnel_name, conn=None, primary=True):
    global prefix
    cmd = prefix+ '{} sudo ip tunnel add {} mode gre remote {} local {} ttl 255'.format(
          name_space, gre_tunnel_name, remote_ip, local_ip)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_default_route_in_namespace(ip_address, interface_name, name_space, conn=None, primary=True):
    ip_address=ip_address.split('/')[0]
    global prefix
    cmd = prefix + '{} ip route add default via {} dev {}'.format(name_space, ip_address, interface_name)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_route_for_gre(ip_address, gre_tunnel_name, conn=None, primary=True):
    ip_address=ip_address.split('/')[0]
    cmd = 'sudo ip route add {} dev {}'.format(ip_address, gre_tunnel_name)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_route_for_gre_cidr_namespace(name_space, cidr, gre_tunnel_name, conn=None, primary=True):
    global prefix    
    cmd = prefix+'{} sudo ip route add {} dev {}'.format(name_space, cidr, gre_tunnel_name)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_route_in_hypervisor(ip_address, interface, conn=None, primary=True):
    ip_address=ip_address.split('/')[0]
    cmd = 'sudo ip route add default via {} dev {}'.format(ip_address, interface)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_route_in_hypervisor_non_default(ip_address, subnet, conn=None, primary=True):
    ip_address=ip_address.split('/')[0]
    cmd = 'sudo ip route add {} via {} '.format(subnet, ip_address)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def add_route_in_namespace_non_default(name_space, ip_address, subnet, conn=None, primary=True):
    global prefix
    ip_address = ip_address.split('/')[0]
    cmd = prefix+'{} ip route add {} via {} '.format(name_space, subnet, ip_address)
    print(cmd)
    if primary == True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return

def add_route_in_namespace(name_space,ip_address,conn=None, primary=True):
    global prefix
    ip_address=ip_address.split('/')[0]
    cmd = prefix+ '{} sudo ip route add default via {}'.format(name_space, ip_address)
    print(cmd)
    if primary==True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return

def add_route_in_namespace_dev(name_space, interface, conn=None, primary=True):
    global prefix
    cmd = prefix + \
        '{} sudo ip route add default dev {}'.format(name_space, interface)
    print(cmd)
    if primary == True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return

def create_vxlan_tunnel(name_space, vxlan_tunnel_name,id,bridge_name,interface,conn=None, primary=True):
    global prefix
    cmd = prefix+ '{} sudo ip link add {} type vxlan id {}  dstport 4789 dev {}'.format(
          name_space, vxlan_tunnel_name, id, interface)
    cmd_1 = prefix + '{} sudo brctl addif {} {}'.format(name_space, bridge_name, vxlan_tunnel_name)
    cmd_2 = prefix + '{} sudo ip link set {} up'.format(name_space, vxlan_tunnel_name)

    cmd_list=[cmd,cmd_1,cmd_2]
    print(cmd_list)
    if primary==True:
        print('local:')
        for cmd in cmd_list:
            os.system(cmd)
        return
    ssh_remote(conn, cmd_list)
    return


def add_fdb_entry_in_vxlan_namespace(name_space, remote_ip, vxlan_dev_name, mac='ff:ff:ff:ff:ff:ff', conn=None, primary=True):
    global prefix
    cmd = prefix + \
        '{} bridge fdb append to {} dst {} dev {} '.format(
            name_space, mac, remote_ip, vxlan_dev_name)
    print(cmd)
    if primary == True:
        print('local:')
        os.system(cmd)
        return
    ssh_remote(conn, [cmd])
    return


def create_bridge_namespace(name_space, bridge_name, conn=None, primary=True):
    global prefix
    cmd = prefix + name_space + ' ip link add name {} type bridge'.format(bridge_name)
    cmd1 = prefix + name_space + \
        ' ip link set dev {} up'.format(bridge_name)
    cmd_list = [cmd, cmd1]
    print(cmd)
    if primary == True:
        print('local:')
        for cmd in cmd_list:
            os.system(cmd)
        return
    ssh_remote(conn, cmd_list)
    return
