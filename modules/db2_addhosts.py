#!/usr/bin/python

import os
import re
class add_hosts:
      def __init__(self, module):
            self.module = module
         
      def parse_params(self):
        self.ip = self.module.params['ip']
        self.host = self.module.params['host']

      def add_hostname(self):
         hosts_param=self.ip+"    "+self.host
         pattern=re.compile(r'^'+self.ip+'(\s+)'+self.host)
         count=0
         file=open('/etc/hosts','r').readlines()
         for i in range(len(file)):
              if re.match(pattern,file[i]):
                   count=count+1
         if count == 0:
              f=open('/etc/hosts','a')
              f.write(hosts_param)
              f.write('\n')
              f.close()
def main():
    global module
    module = AnsibleModule(argument_spec=dict(
            ip=dict(required=True, type='str'),
            host=dict(required=True, type='str')
            )
            ,supports_check_mode=True)
    add=add_hosts(module)
    add.parse_params()
    add.add_hostname()
     
    add.module.exit_json(changed=True, msg="CMD: successed", stdout="", stderr="")

from ansible.module_utils.basic import *
main()

