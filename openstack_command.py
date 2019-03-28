# Copyright 2019 - 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

# -*- coding: utf-8 -*-
import os, subprocess, re

openrc_file = "/root/admin-openrc"

def read_openrc():
    fh= open(openrc_file, "r")
    pdb.set_trace()
    for line in fh.readlines():
        regex = r'^export (OS.+)=(.+)$'
        [(key, value)] = re.findall(regex, line)
        os.environ[key] = value
    return os.environ

def exec_cmd(cmd):
    # export openstack rc
    env = read_openrc()
    p = subprocess.call(cmd,
            env = env,
            shell = True,
            bufsize= 1,
            universal_newlines = True)
    return p

def main():
    # Init
    oscmd_user_list = "/usr/bin/openstack user list"
    exec_cmd(oscmd_user_list)

if __name__ == '__main__':
    main()
