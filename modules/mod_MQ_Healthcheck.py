#!/usr/bin/python

import os
import json
import platform
import commands
import pdb

result_detail = open('/tmp/mqhc_detail.out', 'w+')
overall = 0  # 0 means good, 1 means warning, 2 means critical

class MQ_Healthcheck:

  def __init__(self, module):
    self.module = module
    os.environ['PATH'] = '/opt/mqm/bin:' + os.environ['PATH']
    global result_detail, overall
    self.result_detail = result_detail
    self.overall = overall
  
  def col_version(self):
        mqver_detail = os.popen('dspmqver -a')
	self.result_detail.write("\n#####MQ RESULT#####\n" + mqver_detail.read())
  	cmd = "dspmqver | grep -i version | awk '{print $2}' | head -n 1"
  	rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
  	if stderr!='' or rc !=0:
  	  self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout=stdout)
  	version = stdout.strip('\n')
  	return version
		
  def col_instpath(self):
  
  	cmd = "dspmqver | grep -i instpath | awk '{print $2}' | head -n 1"
  	rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
  	if stderr != '' or rc !=0:
  	  self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
  	instpath = stdout.strip('\n')
  	return instpath
        
  def col_QMGRs(self):
  
    mqqmgrs_detail = os.popen('dspmq -o all')
	self.result_detail.write(mqqmgrs_detail.read())
	
  	cmd = "dspmq | awk '{print $1}' | awk -F '(' '{print $2}' | awk -F ')' '{print $1}'"
  	rc, stdout, stderr=module.run_command(cmd, use_unsafe_shell=True)
  	if stderr != '' or rc !=0:
  	  module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
  	qmgrs = stdout.rstrip('\n').replace('\n', ', ').split(',')
    qmgr_list = []	
	qmgr_dict = {}
    for qmgr in qmgrs:
	  status = {'name':'defalut', 'qmgr': 'Running', 'lstr': 'Running', 'chl': 'Running', 'que': 'Good', 'dlq': 'Good'}
      status['name']=qmgr
	  qmgr_ret = commands.getoutput('dspmq -m ' + qmgr + " | awk '{print $2}' | awk -F '(' '{print $2}' | awk -F ')' '{print $1}'")
	  if 'Running' in qmgr_ret:
    	        lstr_ret = commands.getoutput('ps -ef | grep runmqlsr | grep ' + qmgr + ' | grep -v grep')
		if lstr_ret == '':
		  status['lstr'] = 'Critical'
		chl_ret = commands.getoutput("su - mqm -c \"echo 'dis chs(*) where(status ne running)' | runmqsc " + qmgr + "\"")
		if "RETRYING" in chl_ret or "BINDING" in chl_ret or "In-doubt" in chl_ret:
		  status['chl'] = 'Critical'
		que_ret = commands.getoutput("su - mqm -c \"echo 'dis qs(*) where(curdepth gt 100)' | runmqsc " + qmgr + "\"")
		if "AMQ8450" in que_ret:
		  status['que'] = 'Warning'
		dlq_ret = commands.getoutput("su - mqm -c \"echo 'dis qmgr deadq' | runmqsc " + qmgr + "\"")
		if "DEADQ( )" in dlq_ret:
		  status['dlq'] = 'Warning'
		
		qmgr_detail = os.popen("su - mqm -c \"echo 'dis qmgr' | runmqsc " + qmgr + "\"")
		self.result_detail.write(qmgr_detail.read())
		chl_detail = os.popen("su - mqm -c \"echo 'dis chs(*) all' | runmqsc " + qmgr + "\"")
		self.result_detail.write(chl_detail.read())
	        lstr_detail = os.popen("su - mqm -c \"echo 'dis lsstatus(*) all' | runmqsc " + qmgr + "\"")
		self.result_detail.write(lstr_detail.read())
	        que_detail = os.popen("su - mqm -c \"echo 'dis qs(*) all' | runmqsc " + qmgr + "\"")
		self.result_detail.write(que_detail.read())
	  else:
	    status['qmgr'] = 'Stopped'
		status['lstr'] = 'Stopped'
		status['chl'] = 'Stopped'
		status['que'] = 'Stopped'
		status['dlq'] = 'Stopped'

	  qmgr_list.append(status)
	  qmgr_dict = {}
  	return qmgr_list
  
  def col_system(self):
    cmd = ". /tmp/mqconfig | grep -v mqconfig | grep -E 'PASS|FAIL|WARN' | grep -v shell | awk '{print $1,$(NF-1),$NF}'"
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if stderr != '' or rc !=0:
      module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
    tmp = stdout.rstrip('\n').replace(' ', ':').replace('\n', ',')
    sys_paras = {}
    tmp_list = []
    for l in tmp.split(','):
	  tmp_list = l.split(':')
	  sys_paras[tmp_list[0]] = [tmp_list[1][3:], tmp_list[2]]
	  tmp_list = []
    #sys_paras = dict((l.split(':') for l in tmp.split(',')))
    return sys_paras
  
def main():
    global module
    global result_detail
    result_detail.truncate()
	
    module = AnsibleModule(argument_spec=dict(),supports_check_mode=True)
    mq = MQ_Healthcheck(module)
    json_dict = {'mq': ''}
    version_info = mq.col_version()
    path_info = mq.col_instpath()
    qmgrs_info = mq.col_QMGRs()
    sys_info = mq.col_system()
    json_dict['mq'] = {'Version': version_info, 'InstallPath': path_info, 'QMGRs': qmgrs_info, 'System Paramters': sys_info}
    global overall
    overall_str = str(qmgrs_info)
    if overall_str.find('Critical') != -1 or overall_str.find('Stopped') != -1:
	  json_dict['overall'] = 2
    elif overall_str.find('Warning') != -1:
	  json_dict['overall'] = 1
    else:
	  json_dict['overall'] = 0
    result_detail.close()
    json_str = json.dumps(json_dict)
    mq.module.exit_json(changed=True, msg="CMD: successed", stdout=json_str, stderr="")

from ansible.module_utils.basic import *
main()
