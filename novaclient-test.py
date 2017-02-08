from novaclient import client

#nova_client = client.Client(2,'nova','pass','service','http://192.168.10.5:35357/v3',
nova_client = client.Client(2,'nova','pass',
    auth_url='http://192.168.10.5:35357/v3',
    project_name='service',
    project_domain_name='Default',
    user_domain_name='Default',
    endpoint_type='internalURL',
    service_type="compute",
    region_name='RegionOne')

instances = nova_client.servers.list(search_opts={'all_tenants': 1, 'host': 'devstack'})
print dir(instances)
print instances.x_openstack_request_ids
for i in instances:
    print i.name
    print dir(i)
    print i.hostId
    print i.tenant_id
    print i.id
    print i.status
    print i.__getattr__('OS-EXT-SRV-ATTR:instance_name')
    print i.__getattr__('OS-EXT-AZ:availability_zone')
    print i.created
