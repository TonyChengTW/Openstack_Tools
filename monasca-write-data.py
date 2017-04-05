#!/usr/bin/python
""" This is a tiny tool for generating fake data to send to MonascaAPI then to database.
    Execute the script on the monasca-agent node:
        $ python monasca-write-data.py --keystone_url <keystone_url> [--tenant_id <tenant_id>] [--write_amount <write_amount>]
"""
# Author : Zic
# Version : 0.9
# Copyright(C) 2017 CloudCube Inc., All rights reserved

import argparse
import random
import socket
import time
import monasca_agent.forwarder.api.monasca_api as mon

def parser():
    parser = argparse.ArgumentParser(description='Generating Monasca API requests tool.')
    parser.add_argument('--keystone_url', dest='keystone_url', type=str, required=True,
                        help='Keystone url, e.g. \'http://192.168.141.110:35357/v3\'')
    parser.add_argument('--tenant_id', dest='tenant_id', type=str, required=False, default='service',
                        help='tenant_id here is as an identifier that helps you to find data in database.')
    parser.add_argument('--write_amount', dest='write_amount', type=int, required=False, default=50,
                        help='The number of write queries.')
    return parser.parse_args()

keystone_url = parser().keystone_url
tenant_id = parser().tenant_id
write_amount = parser().write_amount

def gen_data_batch():
    data_batch = []
    # Just contains 10 data in a databatch.
    for loop in range(10):
        data = {'tenant_id': tenant_id,
                'measurement': {
                    'timestamp': time.time() * 1000,
                    'value_meta': None,
                    'dimensions': {
                        'hostname': socket.gethostname(),
                        'component': 'monasca-agent',
                        'service': 'monitoring'
                        },
                    'value': random.uniform(1, 2),
                    'name': 'Measurement-' +str(loop)
                    }
                }
        data_batch.append(data)
    return data_batch


if __name__ == '__main__':
    # The config is stolen from monasca-forwarder. Only keystone_url needs to be provided by you.
    mon_api_config =  {'is_enabled': False, 'max_measurement_buffer_size': -1, 'disable_file_logging': False, 'additional_checksd': '/usr/lib/monasca/agent/custom_checks.d', 'user_domain_name': None, 'use_keystone': True, 'num_collector_threads': 1, 'statsd_log_file': '/var/log/monasca/agent/statsd.log', 'syslog_host': None, 'keystone_timeout': 20, 'max_buffer_size': 1000, 'syslog_port': None, 'limit_memory_consumption': None, 'backlog_send_rate': 1000, 'project_domain_id': None, 'autorestart': True, 'log_level': 'WARN', 'collector_restart_interval': 24, 'listen_port': None, 'check_freq': 30, 'hostname': 'localhost', 'log_to_syslog': False, 'non_local_traffic': False, 'version': '1.6.0', 'jmxfetch_log_file': '/var/log/monasca/agent/jmxfetch.log', 'pool_full_max_retries': 4, 'project_domain_name': None, 'username': 'monasca', 'collector_log_file': '/var/log/monasca/agent/collector.log', 'project_name': 'service', 'skip_ssl_validation': False, 'forwarder_url': 'http://localhost:17123', 'amplifier': 0, 'insecure': False, 'dimensions': {}, 'ca_file': None, 'password': 'nomoresecret', 'sub_collection_warn': 6, 'project_id': None, 'user_domain_id': None, 'url': None, 'keystone_url': keystone_url, 'forwarder_log_file': '/var/log/monasca/agent/forwarder.log', 'write_timeout': 10, 'log_to_event_viewer': False}

    mon_api = mon.MonascaAPI(mon_api_config)
    for wr_amt in range(write_amount):
        message_batch = gen_data_batch()
        mon_api.post_metrics(message_batch)
        print "Write data batch %s, %s left..." % (wr_amt + 1, write_amount - wr_amt - 1)
        time.sleep(1)
