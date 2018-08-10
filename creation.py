from __future__ import print_function
from connection import Connection
import functions
import vmManagement as vmm 
import ipaddress
data_store={'Tenant1':{'NST1':{'interfaces':{'veth1':'192.168.1.1',
'veth3':'192.168.3.1'},
},'NST2':{'interfaces':{'veth2':'192.168.2.1',
'veth4':'192.168.4.1'},

}}}



subnet_hyp1_tenant1=['10.1.0.0/24','10.2.0.0/24']
subnet_hyp2_tenant1=['10.2.0.0/24']

primary_ip_l3='152.46.18.168'
secondary_ip_l3='152.46.18.192'
primary_ip_l2='10.25.7.229'
secondary_ip_l2='10.25.11.143'
isGreCreated=False


def create_tenant(tenant_id=''):
    functions.get_connection()
    tenant_name='T'+str(tenant_id)
    global isGreCreated
    #create namespace PGW-TNAME
    ns_name='PGW-'+tenant_name
    veth_ns = 'pgw-hyp-t'+str(tenant_id)
    veth_hyp='hyp-t'+str(tenant_id)+'-pgw'
    veth_hyp_ip='1.1.'+str(tenant_id)+'.2/24'
    veth_ns_ip='1.1.'+str(tenant_id)+'.1/24'
    functions.create_namespace(ns_name, primary=True)
    #Create veth pair in hypervisor  (pgw-hypt11)(1.1.1.1)(<1.1.tenant-id.1>)
    functions.create_vethpair(veth_hyp,veth_ns,primary=True)

    functions.set_link_up(veth_hyp,primary=True)
    functions.move_veth_to_namespace(veth_ns, ns_name, primary=True)
    functions.assign_ip_address_namespace(ns_name, veth_ns, veth_ns_ip, primary=True)
    functions.set_link_up_in_namespace(ns_name, veth_ns, primary=True)
    functions.assign_ip_address(veth_hyp, veth_hyp_ip, primary=True)
    functions.set_link_up(veth_hyp, primary=True)

    #local ::Another a namespace for tenant (input: tenant_name)
    functions.create_namespace(tenant_name, primary=True)
    veth_pgw_t='pgw_t'+str(tenant_id)
    veth_t_pgw='t'+str(tenant_id)+'_pgw'
    veth_pgw_t_ip='192.168.'+str(tenant_id)+'.1/24'
    veth_t_pgw_ip='192.168.'+str(tenant_id)+'.2/24'
    functions.create_vethpair(veth_pgw_t,veth_t_pgw,primary=True)

    functions.move_veth_to_namespace(veth_pgw_t, ns_name, primary=True)
    functions.assign_ip_address_namespace(ns_name, veth_pgw_t, veth_pgw_t_ip, primary=True)
    functions.set_link_up_in_namespace(ns_name, veth_pgw_t, primary=True)

    functions.move_veth_to_namespace(veth_t_pgw, tenant_name, primary=True)
    functions.assign_ip_address_namespace(tenant_name, veth_t_pgw, veth_t_pgw_ip, primary=True)
    functions.set_link_up_in_namespace(tenant_name, veth_t_pgw, primary=True)

    #remote :: Another a namespace for tenant (input: tenant_name)
    functions.create_namespace(tenant_name, primary=False)

    veth_tenant='t'+str(tenant_id)+'-hyp'
    veth_hyp_t='hyp-t'+str(tenant_id)
    veth_hyp_t_ip='192.168.'+str(tenant_id)+'.1/24'
    veth_tenant_ip='192.168.'+str(tenant_id)+'.2/24'

    functions.create_vethpair(veth_tenant, veth_hyp_t, primary=False)

    functions.move_veth_to_namespace(veth_tenant, tenant_name, primary=False)
    functions.assign_ip_address_namespace(tenant_name, veth_tenant, veth_tenant_ip, primary=False)
    functions.set_link_up_in_namespace(tenant_name, veth_tenant, primary=False)

    functions.assign_ip_address(veth_hyp_t, veth_hyp_t_ip, primary=False)
    functions.set_link_up(veth_hyp_t, primary=False)

    #add default route via 1.1.1.2 in PGW-T1 namespace

    functions.add_default_route_in_namespace(veth_hyp_ip, veth_ns, ns_name, primary=True)

    #add route in tenant namespace as a default route as pgw-t1 in primary

    functions.add_default_route_in_namespace(veth_pgw_t_ip, veth_t_pgw, tenant_name, primary=True)

    #route in remote

    functions.add_default_route_in_namespace(veth_hyp_t_ip, veth_tenant, tenant_name, primary=False)

    # to create a gre tunnel
    if not isGreCreated:
        gre_tunnel_name='GRE-T'+str(tenant_id)
        gre_tunnel_ip_local='11.1.'+str(tenant_id)+'.1/32'
        gre_tunnel_ip_remote='12.1.'+str(tenant_id)+'.1/32'


        #to create a GRE tunnel in primary
        functions.create_gre_tunnel(secondary_ip_l2, primary_ip_l2, gre_tunnel_name, primary=True)
        functions.set_link_up(gre_tunnel_name, primary=True)
        functions.assign_ip_address(gre_tunnel_name, gre_tunnel_ip_local, primary=True)

        functions.add_route_for_gre(gre_tunnel_ip_local, gre_tunnel_name, primary=True)
        functions.add_route_for_gre(gre_tunnel_ip_remote, gre_tunnel_name, primary=True)

        # to create a GRE tunnel in secondary
        functions.create_gre_tunnel(primary_ip_l2, secondary_ip_l2, gre_tunnel_name, primary=False)
        functions.set_link_up(gre_tunnel_name, primary=False)
        functions.assign_ip_address(gre_tunnel_name, gre_tunnel_ip_remote, primary=False)

        functions.add_route_for_gre(gre_tunnel_ip_local, gre_tunnel_name, primary=False)
        functions.add_route_for_gre(gre_tunnel_ip_remote, gre_tunnel_name, primary=False)
        isGreCreated=True

def createVM_primary(tenant_id, subnet_cidr, vm_name, vm_ip):
    conn=functions.get_connection()
    tenant_name='T'+str(tenant_id)
    ip=subnet_cidr.split('/')[0]
    bridge_name=tenant_name+'-br'+ip
    ns_name='PGW-'+tenant_name
    veth_t_pgw_ip='192.168.'+str(tenant_id)+'.2'
    veth_ns_ip='1.1.'+str(tenant_id)+'.1'
    vmm.defineNetwork(conn.primary_conn, bridge_name)
    veth_br_t='br-t'+ip
    veth_t_br='t-br'+ip
    ip_u=unicode(ip,'utf-8')
    veth_t_br_ip=str(ipaddress.ip_address(ip_u)+1)

    functions.create_vethpair(veth_br_t, veth_t_br, primary=True)
    functions.move_veth_to_bridge(veth_br_t, bridge_name, primary=True)
    functions.set_link_up(veth_br_t,primary=True)

    functions.move_veth_to_namespace(veth_t_br, tenant_name, primary=True)
    functions.assign_ip_address_namespace(tenant_name, veth_t_br, veth_t_br_ip, primary=True)
    functions.set_link_up_in_namespace(tenant_name, veth_t_br, primary=True)

    functions.add_route_in_namespace(ns_name,veth_t_pgw_ip, primary=True)

    functions.add_route_in_hypervisor_non_default(veth_ns_ip,subnet_cidr, primary=True)

    functions.create_vm(vm_name,"512",bridge_name,"/tmp/TinyCore.iso", primary=True)

def createVM_secondary_dif_subnet(tenant_id, subnet_cidr, vm_name, vm_ip):
    conn=functions.get_connection()
    tenant_name='T'+str(tenant_id)
    ip=subnet_cidr.split('/')[0]
    bridge_name=tenant_name+'-br'+ip
    veth_tenant_ip='192.168.'+str(tenant_id)+'.2'
    gre_tunnel_name='GRE-T'+str(tenant_id)


    vmm.defineNetwork(conn.secondary_con, bridge_name)
    veth_br_t='br-t'+ip
    veth_t_br='t-br'+ip

    ip_u=unicode(ip,'utf-8')
    veth_t_br_ip=str(ipaddress.ip_address(ip_u)+1)

    functions.create_vethpair(veth_br_t, veth_t_br, primary=False)
    functions.move_veth_to_bridge(veth_br_t, bridge_name, primary=False)
    functions.set_link_up(veth_br_t,primary=False)

    functions.move_veth_to_namespace(veth_t_br, tenant_name, primary=False)
    functions.assign_ip_address_namespace(tenant_name, veth_t_br, veth_t_br_ip, primary=False)
    functions.set_link_up_in_namespace(tenant_name, veth_t_br, primary=False)

    veth_tenant='t'+str(tenant_id)+'-hyp'
    veth_hyp_t='hyp-t'+str(tenant_id)
    veth_hyp_t_ip='192.168.'+str(tenant_id)+'.1/24'
    veth_tenant_ip='192.168.'+str(tenant_id)+'.2/24'

    functions.create_vethpair(veth_tenant, veth_hyp_t, primary=False)

    functions.move_veth_to_namespace(veth_tenant, tenant_name, primary=False)
    functions.assign_ip_address_namespace(tenant_name, veth_tenant, veth_tenant_ip, primary=False)
    functions.set_link_up_in_namespace(tenant_name, veth_tenant, primary=False)

    functions.assign_ip_address(veth_hyp_t, veth_hyp_t_ip, primary=False)
    functions.set_link_up(veth_hyp_t, primary=False)

    functions.add_route_in_hypervisor_non_default(veth_tenant_ip,subnet_cidr, primary=False)

    for subnet in subnet_hyp1_tenant1:
        functions.add_route_for_gre_cidr(subnet, gre_tunnel_name,primary=False)

    for subnet in subnet_hyp2_tenant1:
        functions.add_route_for_gre_cidr(subnet, gre_tunnel_name,primary=True)

    functions.create_vm(vm_name,"512",bridge_name,"/tmp/TinyCore.iso", primary=False)


def createVM_secondary_same_subnet(tenant_id, subnet_cidr, vm_name, vm_ip):
    # tenant bridge on secondary is already created
    conn=functions.get_connection()
    tenant_name='T'+str(tenant_id)
    ip=subnet_cidr.split('/')[0]
    bridge_name=tenant_name+'-br'+ip
    vxlan_tunnel_name='vx_'+tenant_name
    veth_br_t='br-t'+ip
    veth_t_br='t-br'+ip

    ip_u=unicode(ip,'utf-8')
    veth_t_br_ip=str(ipaddress.ip_address(ip_u)+1)

    functions.create_vethpair(veth_br_t, veth_t_br, primary=False)
    functions.move_veth_to_bridge(veth_br_t, bridge_name, primary=False)
    functions.set_link_up(veth_br_t,primary=False)

    functions.move_veth_to_namespace(veth_t_br, tenant_name, primary=False)
    functions.assign_ip_address_namespace(tenant_name, veth_t_br, veth_t_br_ip, primary=False)
    functions.set_link_up_in_namespace(tenant_name, veth_t_br, primary=False)



    functions.create_vxlan_tunnel(secondary_ip_l2, vxlan_tunnel_name, bridge_name, primary=True)

    functions.create_vxlan_tunnel(primary_ip_l2, vxlan_tunnel_name, bridge_name, primary=False)

    functions.create_vm(vm_name,"512",bridge_name,"/tmp/TinyCore.iso", primary=False)


        




        


        

    









    
