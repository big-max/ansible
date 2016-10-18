#!/usr/bin/python

import os
import json
import platform
import commands
import re

class MQ_Sync:

  def __init__(self, module):
    self.module = module
    os.environ['PATH'] = '/opt/mqm/bin:' + os.environ['PATH']
        
  def col_QMGRs(self):
	
    cmd = "dspmq | awk '{print $1}' | awk -F '(' '{print $2}' | awk -F ')' '{print $1}'"
    rc, stdout, stderr=module.run_command(cmd, use_unsafe_shell=True)
    if stderr != '' or rc !=0:
      module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
    qmgrs = stdout.rstrip('\n').replace('\n', ',').split(',')  
   
    if '' in qmgrs:
       return []

    data_list = []
    	
    for qmgr in qmgrs:
  	config_dict = {
              'LogPrimaryFiles': 3, 
	      'LogSecondaryFiles': 2,
	      'LogFilePages': 4096,
	      'LogType': 'CIRCULAR',
	      'MaxChannels': 100,
	      'MaxActiveChannels': 100,
	      'KeepAlive': 'No',
	      'SndBuffSize': 0,
	      'RcvBuffSize': 0,
	      'RcvSndBuffSize': 0,
	      'RcvRcvBuffSize': 0,
	      'ClntSndBuffSize': 0,
	      'ClntRcvBuffSize': 0,
	      'SvrSndBuffSize': 0,
	      'SvrRcvBuffSize': 0,
	      'ErrorLogSize': 2097152
	}
        status = {'type': 'qmgr', 'parent': '-', 'name': '-', 'version': '-'}
                    
        version = commands.getoutput('dspmq -m ' + qmgr + " -o all | awk -F 'INSTVER' '{print $2}'")
        status['version'] = version.replace('(', '').replace(')', '')
        status['name'] = qmgr
	  
        inipath = commands.getoutput('grep \"DataPath.*' + qmgr + "\" /var/mqm/mqs.ini | awk -F '=' '{print $2}'")
        if inipath == '':
          inipath = '/var/mqm/qmgrs/' + qmgr
	  
        file_object = open(inipath + '/qm.ini', 'r')
        config_str = file_object.read()
        for config_item in config_dict.keys():
          search_Obj = re.search(config_item + "=(.+)\n", config_str)
          if search_Obj:
           config_dict[config_item] = search_Obj.group(1)
        file_object.close()
	  
        status['config'] = config_dict
        data_list.append(status)
	  
    return data_list
	
def main():
    global module
	
    module = AnsibleModule(argument_spec=dict(),supports_check_mode=True)
    mq = MQ_Sync(module)
    qmgrs_info = mq.col_QMGRs()
    json_dict = {'product': 'mq', 'data': qmgrs_info}

    json_str = json.dumps(json_dict)
    mq.module.exit_json(changed=True, msg="CMD: successed", stdout=json_str, stderr="")

from ansible.module_utils.basic import *
main()

