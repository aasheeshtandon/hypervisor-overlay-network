#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import libvirt
import jinja2
import yaml
import commands
import functions
from connection import ssh_remote

def getConnection():
    """
    Opens a connection to the local hypervisor
    :return: connection pointer
    """
    conn = libvirt.open('qemu:///system')
    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        return
    else:
        return conn


def listDomInfo(conn):
    """
    :param conn: connection pointer
    lists information about all running domains
    """
    for id in conn.listDomainsID():
        dom = conn.lookupByID(id)
        infos = dom.info()
        print('ID = %d' % id)
        print('Name =  %s' % dom.name())
        print('State = %d' % infos[0])
        print('Max Memory = %d' % infos[1])
        print('Number of virt CPUs = %d' % infos[3])
        print('CPU Time (in ns) = %d' % infos[2])
        print(' ')


def defineNetwork(networkName, conn_libvirt, conn_ssh=None, primary=True):
    """
    Creates a linux-bridge and then activates a persistent VIRSH Network
    :param conn: connection pointer
    :param networkName: name of the Network
    """
    # create a persistent virtual network

    #create the bridge using brctl command
    cmd_1 = "sudo brctl addbr {}".format(networkName)
    cmd_2 = "sudo ip link set {} up".format(networkName)
    cmd_list = [cmd_1, cmd_2]
    if primary == True:
        print('local:')
        for cmd in cmd_list:
            os.system(cmd)
    else:
        ssh_remote(conn_ssh, cmd_list)

    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)
    template_values = {
        'networkName': networkName,
        'bridgeName': networkName,
    }
    template = JINJA_ENVIRONMENT.get_template("bridge.xml")
    finalXML = template.render(template_values)
    filename = '/tmp/%s' %networkName
    with open(filename, 'w') as f:
        f.write(finalXML)
    f.close()

    f = open(filename)
    xmlconfig = f.read()
    #if primary==True:
    network = conn_libvirt.networkDefineXML(xmlconfig)
        
    if network == None:
        print('Failed to create a virtual network', file=sys.stderr)
        return
    network.setAutostart(True)
    network.create()
    print('The new persistent virtual network is active')

def listNetworks(conn, primary=True):
    """
    List all the virtual networks in the hypervisor
    :param conn: connection pointer
    """
    conn = functions.get_connection()
    if primary==True:
        networks = conn.primary_conn.listNetworks()
    else:
        networks = conn.secondary_con.listNetworks()
    print('Virtual networks:')
    for network in networks:
        print('  ' + network)
    print(' ')

    #### If you need to get list of linux virtual bridges uncomment the below lines
    # status, output = commands.getstatusoutput("brctl show | cut -f1")
    # existing = [x for x in output.split("\n")[1:] if x != '']
    # print(existing)


def defineVM(vmIP="192.168.1.2", subnet="24", bridgeName="default"):
    ## old signature: def defineVM(conn, xmlPath)
    """
    Creates a persistent VM and boots it up
    :param conn: connection pointer
    :param xmlPath: absolute path to xml config file as string
    :return:
    """
    userYamlDict = {}
    with open("user-data", 'r') as stream:
        try:
            userYamlDict = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            print("\nUser-data file not found or is empty")
            return

    userYamlDict['runcmd'].insert(0, "ip addr add {0}/{1} dev eth0".format(vmIP, subnet))
    gw = vmIP.split(".")
    gw[-1] = "1"
    gw = ".".join(gw)
    userYamlDict['runcmd'].insert(1, "ip route add default via %s dev eth0" % gw)
    nw = gw.split(".")
    nw[-1] = "0"
    nw = ".".join(nw)
    userYamlDict['runcmd'].insert(2, "ip route add {0}/{1} dev eth0".format(nw, subnet))
    os.system("touch /var/user-data")
    with open('/var/user-data', 'w') as yaml_file:
        yaml.dump(userYamlDict, yaml_file, default_flow_style=False)

    os.system("pip uninstall -y  pyOpenSSL")
    os.system("bash defineVM.sh {0} {1} {2}".format(vmIP, subnet, bridgeName))


    # f = open(xmlPath)
    # xmlconfig = f.read()
    # dom = conn.defineXML(xmlconfig)
    # if dom == None:
    #     print('Failed to define a domain from an XML definition.', file=sys.stderr)
    #     exit(1)
    # if dom.create() < 0:
    #     print('Can not boot guest domain.', file=sys.stderr)
    #     exit(1)
    # print('Guest '+dom.name()+' has booted', file=sys.stderr)
    # f.close()


def main():

    conn = getConnection()
    defineVM(conn,"/home/atandon/sampleVM.xml")
    conn.close()
    exit(0)


if __name__ == "__main__":
    main()

