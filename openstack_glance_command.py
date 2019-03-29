# Copyright 2019 - 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

# -*- coding: utf-8 -*-
import os, subprocess, re
import pdb

openrc_file = "/root/admin-openrc"

def read_openrc():
    fh= open(openrc_file, "r")
    for line in fh.readlines():
        regex = r'^export (OS.+)=(.+)$'
        [(key, value)] = re.findall(regex, line)
        os.environ[key] = value
    fh.close()
    return os.environ

def exec_call(cmd):
    p = subprocess.call(cmd,
            env = read_openrc(),
            shell = True,
            bufsize= 1,
            universal_newlines = True)
    if p != 0:
        exit(1)
    return 0

def exec_popen(cmd):
    p = subprocess.Popen(cmd,
            env = read_openrc(),
            shell = True,
            stdout = subprocess.PIPE,
            bufsize= 1,
            universal_newlines= False)
    return p

def user_create():
    oscmd = 'openstack user create \
              --domain {{ glance_service_domain }} \
              --password {{ glance_service_passwd }} \
              {{ glance_service_user }}'
    return exec_call(oscmd)

def role_add():
    oscmd = 'openstack role add \
                  --project {{ glance_service_project }} \
                  --user {{ glance_service_user }} \
                  {{ glance_service_role }}'
    return exec_call(oscmd)

def service_create():
    oscmd = 'openstack service create --name {{ glance_service_name }} \
              --description "OpenStack Image" image'
    return exec_call(oscmd)

def endpoint_public_create():
    oscmd = 'openstack endpoint create --region RegionOne \
             image internal http://{{ mgmt_ip }}:{{ glance_service_port }}'
    return exec_popen(oscmd)

def endpoint_internal_create():
    oscmd = 'openstack endpoint create --region RegionOne \
             image internal http://{{ mgmt_ip }}:{{ glance_service_port }}'
    return exec_popen(oscmd)

def endpoint_admin_create():
    oscmd = 'openstack endpoint create --region RegionOne \
             image admin http://{{ mgmt_ip }}:{{ glance_service_port }}'
    return exec_popen(oscmd)

# Check function
def user_check():
    oscmd = 'openstack user list | grep {{ glance_service_user }} | wc -l'
    return exec_popen(oscmd)

def role_check():
    oscmd = 'openstack role assignment list --names \
             | grep "{{ glance_service_role }}.*{{ glance_service_user }}@Default" | wc -l'
    return exec_popen(oscmd)

def service_check():
    oscmd = 'openstack service list | grep {{ glance_service_name }} | wc -l'
    return exec_popen(oscmd)

def endpoint_public_check():
    oscmd = 'openstack endpoint list | grep "{{ glance_service_name }}.*public" | wc -l'
    return exec_popen(oscmd)

def endpoint_internal_check():
    oscmd = 'openstack endpoint list | grep "{{ glance_service_name }}.*internal" | wc -l'
    return exec_popen(oscmd)

def endpoint_admin_check():
    oscmd = 'openstack endpoint list | grep "{{ glance_service_name }}.*admin" | wc -l'
    return exec_popen(oscmd)


def main():
    # check user and create user if no exist
    user_check_output = user_check()
    for line in user_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            user_create()

    # check role and add role if no exist
    role_check_output = role_check()
    for line in role_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            role_add()

    # check service and add service if no exist
    service_check_output = service_check()
    for line in service_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            service_create()

    # check endpoint and add endpoint if no exist
    endpoint_public_check_output = endpoint_public_check()
    for line in endpoint_public_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            endpoint_public_create()

    endpoint_internal_check_output = endpoint_internal_check()
    for line in endpoint_internal_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            endpoint_internal_create()

    endpoint_admin_check_output = endpoint_admin_check()
    for line in endpoint_admin_check_output.stdout:
        if line.rstrip('\r\n') == '1':
            break
        else:
            endpoint_admin_create()
    exit(0)

if __name__ == '__main__':
    main()

