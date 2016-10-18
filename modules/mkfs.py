#!/usr/bin/python
import os
import json
import shutil


class mkfs:
     def __init__(self, module):
            self.module = module
            
     def parse_params(self):
        self.pv = self.module.params['pv']
        self.vg = self.module.params['vg']
        self.ppsize = self.module.params['ppsize']
        self.fs = self.module.params['fs']
      
     def scan_disk(self):
         cmd="cfgmgr"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout) 
      
     def check_pv(self,p):
            cmd="lspv|grep -i "+p+" |wc -l"
            rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
            if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
            num=stdout.strip() .strip('\n')
            belong_cmd="lspv|grep -i "+p+" |awk '{print $3}'"
            rc,stdout,stderr=module.run_command(belong_cmd,use_unsafe_shell=True)
            if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % belong_cmd,stderr=stderr, rc=rc, stdout = stdout)
            belong=stdout.strip() .strip('\n')
            if num == "0" or belong != 'None':
          	  return 'false'    
            return 'true' 
            
                
    
     def change_pv(self):
         pvs=self.pv.split(',')
         for p in pvs:
           res=self.check_pv(p)
           if res == 'true':
              cmd="lspv|grep -i "+p+"|awk '{print $2}'"
              rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
              if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
              id=stdout.strip().strip('\n')
              if id == 'none':
                 cmd="chdev -l "+p+" -a pv=yes"
                 rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                 if stderr != '' or rc !=0:
                    module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)  
                
          
          
     def check_vg(self,vg):
         cmd="lsvg|grep -i "+vg+" |wc -l"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         num=stdout.strip().strip('\n')
         if num == "0":
          	return 'true'    
         return 'false'   
        
     def create_vg(self):
     	   res=self.check_vg(self.vg)
     	   if res == 'true':
     	   	  pvs=self.pv.replace(',',' ')
     	   	  cmd="mkvg -s " +self.ppsize+" -y "+self.vg+" -S -n "+pvs
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                  if stderr != '' or rc !=0:
                      module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
            
     
     def check_lv(self,vg,lv):
     	   cmd="lsvg -l "+vg+" |grep -i "+lv+" |wc -l"
     	   rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
           if stderr != '' or rc !=0:
             module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
           num=stdout.strip().strip('\n')
           if num == "0":
          	return 'true'    
           return 'false'  
         
     def create_lv(self):
     	   lvname=self.fs[1:len(self.fs)]+"lv"
     	   res=self.check_lv(self.vg,lvname)
     	   if res == 'true':
     	   	  pvs=self.pv.replace(',',' ')
     	   	  cmd="lsvg "+self.vg+" |grep 'FREE'|awk '{print $6}'"
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	   	  free_pp=int(stdout.strip().strip('\n'))-2
     	   	  crtlv_cmd="mklv -y "+lvname+" -t jfs2 "+self.vg+" "+str(free_pp)+" "+pvs
     	   	  rc,stdout,stderr=module.run_command(crtlv_cmd,use_unsafe_shell=True)
     	   	  if stderr != '' or rc !=0:
                     module.fail_json(changed=False, msg="CMD: %s Failure" % crtlv_cmd,stderr=stderr, rc=rc, stdout = stdout)
              	      	   	           
     
     def check_fs(self,fs):
     	    cmd="lsfs|grep -i "+fs+" |wc -l"
     	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
            if stderr != '' or rc !=0:
               module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
            num=stdout.strip().strip('\n')
            if num == "0":
          	return 'true'    
            return 'false'
        
     def create_fs(self):
     	   res=self.check_fs(self.fs)
     	   if res == 'true':
     	   	  lvname=self.fs[1:len(self.fs)]+"lv"
     	   	  cmd="crfs -v jfs2 -d "+lvname+" -m "+self.fs+" -A no -p rw -a agblksize=4096 -a isnapshot=no"
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	   	  if stderr != '' or rc !=0:
                     module.fail_json(changed=False, msg="CMD: %s Failure" % crtlv_cmd,stderr=stderr, rc=rc, stdout = stdout)
               
               
     def check_mount(self,fs):
         cmd="df -g|grep -i "+fs+" |wc -l"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         num=stdout.strip().strip('\n')
         if num == "0":
          	return 'false'    
         return 'true' 
     
     def mount_fs(self):
     	   res=self.check_mount(self.fs)
     	   if res == 'false':
     	   	  cmd="mount "+self.fs
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                  if stderr != '' or rc !=0:
                       module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
        
        
def main():
    global module
    module = AnsibleModule(argument_spec=dict(
            pv=dict(required=True, type='str'),
            vg=dict(required=True, type='str'),
            ppsize=dict(required=True, type='str'),
            fs=dict(required=True, type='str')
            )
            ,supports_check_mode=True)
    make=mkfs(module)
    make.parse_params()
    make.scan_disk()
    make.change_pv()
    make.create_vg()
    make.create_lv()
    make.create_fs()
    make.mount_fs()
                
    make.module.exit_json(changed=True, msg="CMD: successed", stdout="", stderr="")

from ansible.module_utils.basic import *
main()

