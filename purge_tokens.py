#!/usr/bin/python
# Edit by Tony
# delete tumes of tokens
# Version = 0.1

import time
import subprocess
#import commands


shrink_innodb_cmd = 'mysql -h 192.168.2.10 -u root -pAbc12345 keystone -e "alter table token ENGINE=\'InnoDB\'"'

tokens_purge = {'source': 'source /root/admin-openrc.sh',
                'keystone-manage': 'keystone-manage -v -d token_flush',
                'shrink InnoDB': shrink_innodb_cmd,
               }

for purge_cmd in tokens_purge:
    print '\n\n+++++++ Starting %s : %s  ++++++++++++' % (purge_cmd, tokens_purge[purge_cmd])
    time.sleep(2)
    cli = tokens_purge[purge_cmd]
    print "Command = %s" % cli
    cmd_result = subprocess.call(cli,
                                 shell=True)
#    cmd_result = commands.getstatusoutput(cli)

    print "Result = %s" % cmd_result
