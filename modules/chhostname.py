#!/usr/bin/python

class chhostname:
     def __init__(self, module):
         self.module = module
         
     def get_oldhostname(self):
         cmd="hostname"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout) 
         oldhostname=stdout.strip() .strip('\n')
         return oldhostname
         
     def restart_ha(self):
         cmd="stopsrc -s clcomd; sleep 2; startsrc -s clcomd"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         
         
     def ch_hostname(self):
         newname=self.newhostname
         oldname=self.get_oldhostname()
         if  oldname != newname: 
             cmd1="chdev -l inet0 -a hostname="+newname
             rc,stdout,stderr=module.run_command(cmd1,use_unsafe_shell=True)
             if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd1,stderr=stderr, rc=rc, stdout = stdout) 
             cmd2="uname -S "+newname
             rc,stdout,stderr=module.run_command(cmd2,use_unsafe_shell=True)
             if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd2,stderr=stderr, rc=rc, stdout = stdout) 
             cmd3="hostname "+newname
             rc,stdout,stderr=module.run_command(cmd3,use_unsafe_shell=True)
             if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd3,stderr=stderr, rc=rc, stdout = stdout) 
             self.restart_ha()
             
                       
      
            
     def parse_params(self):
        self.newhostname = self.module.params['name']
           

def main():
    global module
    module = AnsibleModule(argument_spec=dict(
            name=dict(required=True, type='str'),
            )
            ,supports_check_mode=True)
    chhost=chhostname(module)
    chhost.parse_params()
    chhost.ch_hostname()
    chhost.module.exit_json(changed=True, msg="CMD: successed", stdout="", stderr="")

from ansible.module_utils.basic import *
main()

