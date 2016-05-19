#!/usr/bin/python
# Edit by Tony
# delete tumes of tokens
# Version = 0.1

import subprocess
import time


shrink_innodb_cmd = 'mysql -h 192.168.2.10 -u root -pAbc12345 keystone -e "alter table token ENGINE=\'InnoDB\'"'
tokens_purge = {'keystone-manage': 'source /root/admin-openrc.sh;keystone-manage -v -d token_flush', 
                'shrink InnoDB': shrink_innodb_cmd,
               }

for purge_cmd in tokens_purge:
    print '\n\n+++++++ Starting %s : %s  ++++++++++++' % (purge_cmd, tokens_purge[purge_cmd])
    time.sleep(2)
    cli = tokens_purge[purge_cmd]
    print "Command = %s" % cli
#    cmd_result = subprocess.check_output(cli,
#                                         stderr=subprocess.STDOUT,
#                                         shell=True)
    cmd_result = subprocess.call(cli,
                                 shell=True,
                                 executable="/bin/bash",
                                )
    print "Result = %s" % cmd_result
