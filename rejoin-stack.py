#!/usr/bin/python
# Edit by Tony
# Replace rejoin-stack.sh
# Version v0.1

import time
import commands


os_services = {'nova-api': '/usr/local/bin/nova-api',
               'nova-compute': 'sg libvirtd /usr/local/bin/nova-compute --config-file /etc/nova/nova.conf'}

for service_key in os_services:
    print '\n\n+++++++++++++ starting %s : %s++++++++++++++++++' % service_key, os_services[service_key]
    time.sleep(2)
    cli = 'screen -t os_services[service_key] -s os_services[service_key]'
    cmd_result = commands.getstatusoutput(cli)
    print cmd_result

