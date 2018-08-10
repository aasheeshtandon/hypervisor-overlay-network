import commands
import os

import functions
import tenant_management
from connection import Connection

conn = None
conn = functions.get_connection()


def delete_namespace(primary=True):
    if primary == True:
        print('local:')
        os.system("sudo ip -all netns delete")
        return
    conn.ssh_remote(["sudo ip -all netns delete"])
    return


def delete_veth(primary=True):
    if primary == True:
        print('local:')
        status, output = commands.getstatusoutput("ifconfig -a| grep Y | awk '{ print $1}'")
        existing = [x for x in output.split("\n")]
        for i in existing:
            cmd = "sudo ip link delete {}".format(i)
            os.system(cmd)
        return
    else:
        ret = conn.ssh_remote(["ifconfig -a | grep veth | awk '{ print $1}'"])
        print("ret : {} type: {}".format(ret, type(ret)))
        existing = ret[0].split("\n")
        for i in existing:
            cmd = "sudo ip link delete {}".format(i)
            conn.ssh_remote([cmd])
        return


def delete_bridge(primary=True):
    import pdb
    pdb.set_trace()
    if primary == True:
        status, output = commands.getstatusoutput("brctl show | cut -f1")
        existing = [x for x in output.split("\n")]
        for i in existing[1:]:
            if i != 'virbr0' and i != '':
                cmd1 = "sudo ip link set dev {} down".format(i)
                cmd2 = "sudo brctl delbr {}".format(i)
                os.system(cmd1)
                os.system(cmd2)
        return
    else:
        ret = conn.ssh_remote(["brctl show | cut -f1"])
        existing = ret[0].split("\n")
        for i in existing[1:]:
            if i != 'virbr0' and i != '':
                cmd1 = "sudo ip link set dev {} down".format(i)
                cmd2 = "sudo brctl delbr {}".format(i)
                conn.ssh_remote([cmd1])
                conn.ssh_remote([cmd2])
        return


def delete_network(primary=True):
    if primary == True:
        status, output = commands.getstatusoutput("ls -l /etc/libvirt/qemu/networks/ | awk '{print $9}'")
        existing = [x for x in output.split("\n")]
        for i in existing[3:]:
            cmd1 = "sudo virsh net-destroy {}".format(i[:-4])
            cmd2 = "sudo virsh net-undefine {}".format(i[:-4])
            os.system(cmd1)
            os.system(cmd2)
        return
    else:
        ret = conn.ssh_remote(["ls -l /etc/libvirt/qemu/networks/ | awk '{print $9}'"])
        existing = ret[0].split("\n")
        for i in existing[3:]:
            cmd1 = "sudo virsh net-destroy {}".format(i[:-4])
            cmd2 = "sudo virsh net-undefine {}".format(i[:-4])
            conn.ssh_remote([cmd1])
            conn.ssh_remote([cmd2])
        return


def delete_routes(primary=True):
    if primary == True:
        status, output = commands.getstatusoutput("ip route | grep 10.2.* | awk '{print $1}' ")
        existing = [x for x in output.split("\n")]
        for i in existing:
            cmd = "sudo ip route delete {}".format(i)
            os.system(cmd)
        return
    else:
        ret = conn.ssh_remote(["ip route | grep 10.2.* | awk '{print $1}' "])
        existing = ret[0].split("\n")
        for i in existing:
            cmd = "sudo ip route delete {}".format(i)
            conn.ssh_remote([cmd])
        return


def delete_gre(primary=True):
    if primary == True:
        status, output = commands.getstatusoutput("ip addr | grep GRE* | awk '{print $2}' ")
        existing = [x for x in output.split("\n")]
        for i in existing:
            cmd = "sudo ip tunnel delete {}".format(i[:-6])
            os.system(cmd)
        return
    else:
        ret = conn.ssh_remote(["ip addr | grep GRE* | awk '{print $2}' "])
        existing = ret[0].split("\n")
        for i in existing:
            cmd = "sudo ip tunnel delete {}".format(i[:-6])
            conn.ssh_remote([cmd])
        return

def delete_vxlan(primary=True):
    if primary == True:
        status, output = commands.getstatusoutput("ip addr | grep vx_* | awk '{print $2}'")
        existing = [x for x in output.split("\n")]
        for i in existing:
            cmd = "sudo ip link delete dev {}".format(i[:-1])
            os.system(cmd)
        return
    else:
        ret = conn.ssh_remote(["ip addr | grep vx_* | awk '{print $2}' "])
        existing = ret[0].split("\n")
        for i in existing:
            cmd = "sudo ip link delete dev {}".format(i[:-1])
            conn.ssh_remote([cmd])
        return

def delete_vm(primary=True):
    if primary == True:
        status, output = commands.getstatusoutput("ls -l /etc/libvirt/qemu/ | awk '{print $9}'")
        existing = [x for x in output.split("\n")]
        for i in existing[1:]:
            if i != 'networks' and i != '':
                cmd1 = "sudo virsh destroy {}".format(i[:-4])
                cmd2 = "sudo virsh undefine {}".format(i[:-4])
                os.system(cmd1)
                os.system(cmd2)
        return
    else:
        ret = conn.ssh_remote(["ls -l /etc/libvirt/qemu/ | awk '{print $9}'"])
        existing = ret[0].split("\n")
        for i in existing[1:]:
            if i != 'networks' and i != '':
                cmd1 = "sudo virsh net-destroy {}".format(i[:-4])
                cmd2 = "sudo virsh net-undefine {}".format(i[:-4])
                conn.ssh_remote([cmd1])
                conn.ssh_remote([cmd2])
        return


def main():
    primary=True
    
    delete_namespace(primary)
    delete_veth(primary)
    delete_bridge(primary)
    delete_network(primary)
    delete_routes(primary)
    delete_vm(primary)
    delete_gre(primary)
    delete_vxlan(primary)

    primary = False

    delete_namespace(primary)
    delete_veth(primary)
    delete_bridge(primary)
    delete_network(primary)
    delete_routes(primary)
    delete_vm(primary)
    delete_gre(primary)
    delete_vxlan(primary)

    

if __name__ == '__main__':
    main()
