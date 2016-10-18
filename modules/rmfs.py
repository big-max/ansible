#!/usr/bin/python
import os
import json
import shutil


class rmfs:
     def __init__(self, module):
            self.module = module
            
     def parse_params(self):
        self.pv = self.module.params['pv']
        self.vg = self.module.params['vg']
        self.fs = self.module.params['fs']
      
          
     def check_vg(self,vg):
         cmd="lsvg|grep -i "+vg+" |wc -l"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         num=stdout.strip().strip('\n')
         if num == "0":
          	return 'false'    
         return 'true'   
        
     def drop_vg(self):
     	   res=self.check_vg(self.vg)
     	   if res == 'true':
     	   	  pvs=self.pv.split(',')
     	   	  self.varyon_vg(self.vg)
     	   	  for p in pvs:
     	   	    cmd="reducevg -d -f " +self.vg+" "+p
     	   	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                    if stderr != '' or rc !=0:
                       module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
               
     def check_varyon(self,vg):
     	 cmd="lspv|grep "+self.vg+" |head -n 1 |awk '{print $4}'"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         is_varyon=stdout.strip().strip('\n')
         if is_varyon == 'active':
         	  return 'true'
         return 'false'
         
     def varyon_vg(self,vg):
     	   res=self.check_varyon(vg)
     	   if res == 'false':
     	      cmd="varyonvg "+vg
     	      rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
              if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
     
     def varyoff_vg(self,vg):
           res=self.check_varyon(vg)
     	   if res == 'true':
     	      cmd="varyoffvg "+vg
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
          	return 'false'    
        return 'true'  
         
     def drop_lv(self):
     	   lvname=self.fs[1:len(self.fs)]+"lv"
     	   res=self.check_lv(self.vg,lvname)
     	   if res == 'true':
     	   	  cmd="rmlv -f "+lvname
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	   	  if stderr != '' or rc !=0:
                     module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
              	      	   	           
     
     def check_fs(self,fs):
     	  cmd="lsfs|grep -i "+fs+" |wc -l"
     	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
          if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
          num=stdout.strip().strip('\n')
          if num == "0":
          	return 'false'    
          return 'true'
        
     def drop_fs(self):
     	   res=self.check_fs(self.fs)
     	   if res == 'true':
     	   	  cmd="rmfs  "+self.fs
     	   	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	   	  if stderr != '' or rc !=0:
                      module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
     
     def umount_fs(self):
          res=self.check_mount(self.fs)
          if res == 'true':
             cmd="umount -f "+self.fs
             rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	     if stderr != '' or rc !=0:
               module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
             
         
     def check_mount(self,fs):
         cmd="df -g|grep -i "+fs+" |wc -l"
         rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
         if stderr != '' or rc !=0:
            module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         num=stdout.strip().strip('\n')
         if num == "0":
          	return 'false'    
         return 'true'  
        
def main():
    global module
    module = AnsibleModule(argument_spec=dict(
            pv=dict(required=True, type='str'),
            vg=dict(required=True, type='str'),
            fs=dict(required=True, type='str')
            )
            ,supports_check_mode=True)
    remv=rmfs(module)
    remv.parse_params()
    remv.umount_fs()
    remv.drop_fs()
    remv.drop_lv()
    remv.drop_vg()
                
    remv.module.exit_json(changed=True, msg="CMD: successed", stdout="", stderr="")

from ansible.module_utils.basic import *
main()

