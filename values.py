import json
from pprint import pprint
import copy
        
#ssh-copy-id ckogant@152.46.20.10
#ssh-copy-id ckogant@152.46.18.27

def get_value():
    primary_data = {
        'username': 'sbansal3',
        'ip': '152.46.20.80',
        'l2_ip': '10.25.7.241'
    }
    secondary_data = {
        'username': 'sverma4',
        'ip': '152.46.18.67',
        'l2_ip': '10.25.11.155'
    }
    tertiary_data = {
        'username': 'sbansal3',
        'ip': '152.46.16.66',
        'l2_ip': '10.25.7.184'
    }
    return primary_data, secondary_data, tertiary_data

def get_user_data():
    user_data = None
    """
    with open("user_data.json", 'r') as f:
        user_data = json.load(f)
    pprint(user_data)
    """
    return convert_data()

def convert_data():
    user_input = None
    with open("user_input.json", 'r') as f:
        user_input = json.load(f)
    pprint(user_input)
    list_tenants = user_input["data"]["tenants"]
    tenant_blank = {u'id': u'',
                    u'primary': {u'subnets': []},
                    u'secondary': {u'subnets': []},
                    u'tertiary': {u'subnets': []}
                    }
    user_data = {u'data': {u'tenants': [] 
                            }
                }

    for tenant in list_tenants: 
        list_subnets = tenant['subnets']
        #print("tenant_id: {}".format(tenant['id']))
        copy_tenant_data = copy.deepcopy(tenant_blank)
        copy_tenant_data['id'] = tenant['id']
        #pprint(list_subnets)
        subnets = {}
        for item in list_subnets:
            subnets[item['cidr']] = item['vm_ips']
        #print(subnets)
        max_len = 0
        max_len_subnet = None
        max_subnet = {}
        for subnet in subnets:
            len_ = len(subnets[subnet])
            if len_>max_len:
                max_len = len_
                max_len_subnet = subnet
        max_subnet[max_len_subnet] = subnets[max_len_subnet]
        #print(max_subnet)
        del subnets[max_len_subnet]
        #pprint(subnets)
        flag = 0
        max_data_p = dict()
        max_data_p['cidr'] = max_len_subnet
        max_data_p['vm_ips'] = max_subnet[max_len_subnet][0::3]
        max_data_s = dict()
        max_data_s['cidr'] = max_len_subnet
        max_data_s['vm_ips'] = max_subnet[max_len_subnet][1::3]
        max_data_t = dict()
        max_data_t['cidr'] = max_len_subnet
        max_data_t['vm_ips'] = max_subnet[max_len_subnet][2::3]
        #print(max_data_p)
        #print(max_data_s)
        #print(max_data_t)
        for i, subnet in enumerate(subnets):
            cidr = subnet
            vm_ips = subnets[subnet]
            data = dict() 
            data['cidr'] = cidr
            data['vm_ips'] = vm_ips
            if i%3 == 0:
                copy_tenant_data['primary']['subnets'].append(data)      
            elif i % 3 == 1:
                copy_tenant_data['secondary']['subnets'].append(data)
            else:
                copy_tenant_data['tertiary']['subnets'].append(data)
            if flag == 0:
                copy_tenant_data['primary']['subnets'].append(max_data_p) 
                copy_tenant_data['secondary']['subnets'].append(max_data_s)
                copy_tenant_data['tertiary']['subnets'].append(max_data_t)
                flag = 1
        user_data['data']['tenants'].append(copy_tenant_data)
        #pprint(copy_tenant_data)
    
    pprint(user_data)
    return user_data


            
        

        
             

        

    
    




    #
    # user_data = {
    #     'data': {
    #         'tenants': [{
    #             'id': "3",
    #             'primary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.3", "1.2.2.4"],
    #                     "vm_data":{'1.2.2.3':'aa',
    #                                '1.2.2.4':'bb'},
    #                 }, {
    #                     "cidr": "1.5.5.0/24",
    #                     "vm_ips": ["1.5.5.2"],
    #                 }]
    #             },
    #             'secondary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.5"],
    #                 }, {
    #                     "cidr": "1.6.6.0/24",
    #                     "vm_ips": ["1.6.6.2"],
    #                 }
    #
    #                 ]
    #             },
    #             'tertiary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.5"],
    #                 }, {
    #                     "cidr": "1.6.6.0/24",
    #                     "vm_ips": ["1.6.6.2"],
    #                 }
    #
    #                 ]
    #             }
    #
    #         },
    #             {
    #             'id': "4",
    #             'primary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.3"],
    #                 }, {
    #                     "cidr": "1.5.5.0/24",
    #                     "vm_ips": ["1.5.5.2"],
    #                 }]
    #             },
    #             'secondary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.5"],
    #                 }, {
    #                     "cidr": "1.6.6.0/24",
    #                     "vm_ips": ["1.6.6.2"],
    #                 }
    #
    #                 ]
    #             },
    #             'tertiary': {
    #                 "subnets": [{
    #                     "cidr": "1.2.2.0/24",
    #                     "vm_ips": ["1.2.2.5"],
    #                 }, {
    #                     "cidr": "1.6.6.0/24",
    #                     "vm_ips": ["1.6.6.2"],
    #                 }
    #
    #                 ]
    #             }
    #         }]}}
