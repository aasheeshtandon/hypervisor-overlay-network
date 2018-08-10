# hypervisor-overlay-network
Hypervisor Overlay Networking as a Service
Creating multipoint tunnels (GRE & VXLAN) between different hypervisors for connecting VMs of tenants.  
1. Run env.sh file in all your hypervisors
2. create_tenant(tenant_id='')
    - It will create a tenant in Primary hypervisor

3. createVM_primary(tenant_id, subnet_cidr, vm_name, vm_ip)
    - This method is used to create VM in primary hypervisor for any tenant.
4. createVM_secondary_dif_subnet(tenant_id, subnet_cidr, vm_name, vm_ip)
    - This method is used to create VM in secondary hypervisor for any tenant.
    - This will provide L3 connectivity across multiple hypervisors.
    - Using GRE
5. createVM_secondary_same_subnet(tenant_id, subnet_cidr, vm_name, vm_ip)
    - This method is used to create VM in secondary hypervisor for any tenant.
    - This will provide L2 connectivity across multiple hypervisors.
    - Using VXLAN

You will need to call these methods manually in test_connection.py