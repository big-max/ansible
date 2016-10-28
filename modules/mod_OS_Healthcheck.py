#!/usr/bin/python

import glob,errno,os
import json
import platform
import commands
import psutil
import time
import socket
import sys
import pdb
import subprocess as subp

result_detail = open('/tmp/oshc_detail.out', 'w+')
overall = 0  # 0 means good, 1 means warning, 2 means critical

class OS_Healthcheck:

  def __init__(self, module):
    self.module = module		
    global result_detail, overall
    self.result_detail = result_detail
    self.overall = overall
	
  def col_basic(self):
    basic_dict = {'Hostname': '', 'Version': '', 'IP': '', 'Start': ''}
    basic_dict['Version'] = platform.platform()
    basic_dict['Hostname'] = socket.getfqdn(socket.gethostname())
    basic_dict['IP'] = socket.gethostbyname(basic_dict['Hostname'])
    basic_dict['Start'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(psutil.boot_time())) 
	
    if platform.platform().find('Linux') != -1:
      detail = os.popen('date;echo;uptime;echo;hostname;echo;lsb_release -a')
    else:
      detail = os.popen('date;echo;uptime;echo;hostname;echo;oslevel -s;echo;errpt;echo;prtconf')
	  
    self.result_detail.write("\n#################Basic Information#################\n" + detail.read())
    
    return basic_dict

  def get_status(self, cur_value, warn, error):
    if cur_value < warn:
      return 'GOOD'
    if cur_value >= warn and cur_value < error:
      return 'WARN'
    if cur_value >= error:
      return 'BAD'
  
  def col_runtime(self):
    cpu_total, memory_total, swap_total, disk_high = 0, 0, 0, 0
    runtime_dict = {'CPU': '', 'RAM': '', 'Swap': '', 'Disk': ''}
	
    for x in range(5):
      cpu_total += psutil.cpu_percent(interval=2)
      memory_total += psutil.virtual_memory().percent
      swap_total += psutil.swap_memory().percent
	
    for i in psutil.disk_partitions():
      if psutil.disk_usage(i[1])[3] > 85.0 and psutil.disk_usage(i[1])[3] > disk_high:
        disk_high = psutil.disk_usage(i[1])[3]
	
    cpu_usage = ("%.2f" % float(cpu_total/5))
    ram_usage = ("%.2f" % float(memory_total/5))
    swap_usage = ("%.2f" % float(swap_total/5))
    disk_usage = ("%.2f" % float(disk_high))
	
    runtime_dict['CPU'] = ['WARN 50 BAD 70', cpu_usage, self.get_status(float(cpu_usage), 50, 70)]
    runtime_dict['RAM'] = ['WARN 70 BAD 90', ram_usage, self.get_status(float(ram_usage), 70, 90)]
    runtime_dict['Swap'] = ['WARN 30 BAD 50', swap_usage, self.get_status(float(swap_usage), 30, 50)]
    runtime_dict['Disk'] = ['WARN 80 BAD 90', disk_usage, self.get_status(float(disk_usage), 80, 90)]
	
    all_status = [runtime_dict['CPU'][2], runtime_dict['RAM'][2], runtime_dict['Swap'][2], runtime_dict['Disk'][2]]
    if 'BAD' in all_status:
      self.overall = 2
    elif 'WARN' in all_status:
      self.overall = 1
    else:
      self.overall = 0
	
    if platform.platform().find('Linux') != -1:
      detail = os.popen("vmstat 2 10;echo;iostat -m 2 10;echo;netstat -n | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}';echo; free -m;echo;df -lh")
    else:
      detail = os.popen("vmstat 2 10;echo;iostat -m 2 10;echo;netstat -n | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}';echo; svmon -G -i 2 5;echo;df -g;echo; lsps -a")
	
    self.result_detail.write("\n#################Runtime Information#################\n" + detail.read())
	
    return runtime_dict
	
  def col_top10(self, count=0):
    j_top10process = {}
    local_count = count
    p = subp.Popen('ps -eo pcpu,pid,user,comm,etime | sort -r -k1 | head -11', stdout=subp.PIPE, stderr=subp.PIPE,shell=True)
    output, errors = p.communicate()
    if errors:
      local_count += 1
      if local_count < 4:
        return j_top10processes(local_count)
      else:
        return {"error": "tried 4 times to calculate top 10 processes."}
    processes = output.split('\n')
    for process_num in range(1,11):
        process = processes[process_num].split()
        item = {
            'CPU': process[0],
            'PID':process[1],
            'USER': process[2],
            'COMMAND': process[3],
            'ELAPSED': process[4]
        }
        j_top10process.update({process_num: item})
	
    if platform.platform().find('Linux') != -1:
      detail = os.popen('ps auxw --sort=%cpu;echo;ps -ef |grep defunc')
    else:
      detail = os.popen('ps auxw | sort -rn +2;echo;ps -ef |grep defunc')
	
    self.result_detail.write("\n#################Process Information#################\n" + detail.read())
	
    return j_top10process

  def col_env(self):
    cmd = "env | sort -r"
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if stderr != '' or rc !=0:
      self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
    env = stdout.strip('\n')
	
    return env
  
  def col_cron(self):
    try:
        path = '/var/spool/cron/*'
        files = glob.glob(path)
        j_crons = {}
        for name in files:
            file_content = []
            try:
                with open(name) as file:
                    for line in file.readlines():
                        if not line.startswith('#'):
                            if not line.startswith('\n'):
                                file_content.append(line.replace('\n',''))
                j_crons.update({name : file_content} )
            except IOError as exc:
                if exc.errno != errno.EISDIR:
                    raise
    except Exception,error:
        j_crons =  { "error" : error }
		
    return j_crons
	
def main():
    global module
    global result_detail
    result_detail.truncate()
    module = AnsibleModule(argument_spec=dict(),supports_check_mode=True)
    os_obj = OS_Healthcheck(module)
    json_dict = {}
    basic_info = os_obj.col_basic()
    runtime_info = os_obj.col_runtime()
    top10_info = os_obj.col_top10()
    cron_info = os_obj.col_cron()
    env_info = os_obj.col_env()
    json_dict = {
      'status': overall,
      'os': {
        "basic": basic_info,
        "cronjobs": cron_info,
        "env": env_info,
        "top10": top10_info,
        "runtime": runtime_info
      }
    }
    result_detail.close()
    json_str = json.dumps(json_dict)
    os_obj.module.exit_json(changed=True, msg="CMD: successed", stdout=json_str, stderr="")

from ansible.module_utils.basic import *
main()
