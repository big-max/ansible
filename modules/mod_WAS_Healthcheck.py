#!/usr/bin/python

import os
import json
import platform
import commands
import pdb

result_detail = open('/tmp/washc_detail.out', 'w+')
overall = 0  # 0 means good, 1 means warning, 2 means critical

class WAS_Healthcheck:

  def __init__(self, module):
    self.module = module
    global result_detail, overall
    self.result_detail = result_detail
    self.overall = overall

  def col_basic(self):
  
    instpath = str(commands.getoutput("ps -ef|grep java| grep -v grep | awk '{print $8}' | uniq | head -n 1"))[:-14]
    version = commands.getoutput(instpath+"/bin/versionInfo.sh  | grep Version | grep -v version | awk '{print $2}'")
    jdk = commands.getoutput(instpath+"/java/bin/java -fullversion")
    user = commands.getoutput("ps -ef|grep java| grep -v grep | awk '{print $1}' | uniq | head -n 1")

    wasbasic_detail = os.popen('ps -ef | grep java;'+instpath+"/bin/versionInfo.sh")
    self.result_detail.write("\n#####WAS Process#####\n" + wasbasic_detail.read())
	
    basic = {'instpath': instpath, 'version': version, 'jdk': jdk, 'user': user}
    return basic
  
  def col_version(self, instpath):
  
    wasver_detail = os.popen(instpath+'/bin/versionInfo.sh')
    self.result_detail.write("\n#####WAS RESULT#####\n" + wasver_detail.read())

    cmd = instpath+"/bin/versionInfo.sh  | grep Version | grep -v version | awk '{print $2}'"	
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if stderr!='' or rc !=0:
      self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout=stdout)
    version = stdout.strip('\n')
    return version 
		
  def col_instpath(self):
  
    cmd = "ps -ef|grep java| grep -v grep | awk '{print $8}' | uniq | head -n 1"
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if stderr != '' or rc !=0:
      self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
    instpath = str(stdout.strip('\n'))[:-14]
    self.instpath = instpath
    return instpath
        
def main():
    global module
    global result_detail
    result_detail.truncate()
	
    module = AnsibleModule(argument_spec=dict(),supports_check_mode=True)
    was = WAS_Healthcheck(module)
    json_dict = {'was': ''}
    path_info = was.col_instpath()
    version_info = was.col_version(path_info)
   # qmgrs_info = mq.col_QMGRs()
   # sys_info = mq.col_system()
   # json_dict['mq'] = {'Version': version_info, 'InstallPath': path_info, 'QMGRs': qmgrs_info, 'System Paramters': sys_info}
    json_dict['mq'] = {'basic': was.col_basic()}
	
    global overall
    overall_str = str("aaa")
    if overall_str.find('Critical') != -1:
      json_dict['overall'] = 2
    elif overall_str.find('Warning') != -1:
      json_dict['overall'] = 1
    else:
      json_dict['overall'] = 0

    result_detail.close()
    json_str = json.dumps(json_dict)
    was.module.exit_json(changed=True, msg="CMD: successed", stdout=json_str, stderr="")

from ansible.module_utils.basic import *
main()
