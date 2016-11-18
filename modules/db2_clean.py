#!/usr/bin/python
import os
import json
import shutil


class db2_clean:
     def __init__(self, module):
            self.module = module
     
     def is_db2_alreadby_installed(self):     	   
     	   return os.path.exists(self.base)  
                	    

     def is_user_exits(self,user):
     	    cmd="grep "+user+" /etc/passwd|wc -l" 
     	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
            if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
            num=stdout.strip()          
            if num != "0":
          	  return 'true'
            return 'false'
     
     def clean_user(self):
     	    for users in self.inst,self.fenc:
     	    	 res=self.is_user_exits(users)
     	    	 if res == 'true':
     	    	 	  cmd="rmuser -p "+users
     	    	 	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                          if stderr != '' or rc !=0:
                             module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)    
                          else:
                             home=os.path.join('/home',users)
                	     shutil.rmtree(home)

                             
     def is_group_exits(self,group):
          cmd="grep "+group+" /etc/group|wc -l" 
          rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
          if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
          num=stdout.strip()          
          if num != "0":
          	  return 'true'
          return 'false'
          
     def clean_group(self):
     	    for groups in self.inst_group,self.fenc_group:
     	    	 res=self.is_group_exits(groups)
     	    	 if res == 'true':
     	    	 	  cmd="rmgroup "+groups
     	    	 	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
                          if stderr != '' or rc !=0:
                              module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)        
     
     
 	        
     def is_inst_already_created(self):
     	  cmd=self.base+"/bin/db2ilist|grep -i "+self.inst+"|wc -l"
     	  rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
          if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
          num=stdout.strip()
          if num != "0":
          	 return 'true'
          return 'false'
          
     def clean_inst(self):
     	    if self.is_db_already_created() == 'true':
     	    	 if self.instance_up() == 'true':
     	    	 	   self.clean_db()
     	    	 else:
     	    	 	  self.start_instance()
     	    	 	  self.clean_db()
     	    
     	    if self.instance_up() == 'true':
     	    	  self.stop_instance()
     	         	    	 
     	    cmd=self.base+"/instance/db2idrop "+self.inst
     	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	    if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
     
     def clean_db2(self):
     	    if self.is_inst_already_created() == 'true':
     	       self.clean_inst()
     	    cmd=self.base+"/install/db2_deinstall -a"
     	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	    if  rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
                    
     def is_db_already_created(self):
           cmd="su - " + self.inst + " -c 'db2 list db directory|grep -i  "+ self.db +" '|wc -l"
           rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
           if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
           num=stdout.strip()
           if num != "0":
           	 return 'true'
           return 'false'
           	   
     def clean_db(self):
            cmd="su - "+ self.inst +" -c 'db2 force applications all;db2 deactivate db " + self.db + ";db2 drop db "+ self.db + " '"
     	    rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
     	    if stderr != '' or rc !=0:
              module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
           	  
                      
     def instance_up(self):
        cmd = "ps -ef | grep " +self.inst + "| grep db2sysc | grep -v grep | wc -l" 
        rc, stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
        if stderr:
            self.module.fail_json(changed=False, msg='Could not validade if instance is up', stderr=stderr, rc=rc, stdout=stdout)
        num=stdout.strip()
        if num != "0":
           return 'true'
        return 'false'
      
     def start_instance(self):
     	   cmd="su - "+ self.inst +" -c 'db2start '"
     	   rc, stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
     	   if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
         
     def stop_instance(self):
     	   cmd="su - "+ self.inst +" -c 'db2stop force'"
     	   rc, stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
     	   if stderr != '' or rc !=0:
                 module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)
                 
     def clean_path(self):
           bin_path=self.binpath+'/'+self.version
     	   if os.path.exists(bin_path) and  bin_path != '/':
     	     	   shutil.rmtree(bin_path)
     
       
     def parse_params(self):
        self.db = self.module.params['db']
        self.inst = self.module.params['inst']
        self.base = self.module.params['base']
        self.fenc = self.module.params['fenc']
        self.inst_group = self.module.params['inst_group']
        self.fenc_group = self.module.params['fenc_group']
        self.version = self.module.params['version']
        self.binpath = self.module.params['binpath']
        self.logpath = self.module.params['logpath']
        self.archpath = self.module.params['archpath']
        self.dbpath = self.module.params['dbpath']
        self.datapath = self.module.params['datapath'] 

def main():
    global module
    module = AnsibleModule(argument_spec=dict(
            inst=dict(required=True, type='str'),
            db=dict(required=True, type='str'),
            base=dict(required=True, type='str'),
            fenc=dict(required=True,type='str'),
            inst_group=dict(required=True,type='str'),
            fenc_group=dict(required=True,type='str'),
            version=dict(required=True,type='str'),
            binpath=dict(required=True,type='str'),
            logpath=dict(required=True,type='str'),
            archpath=dict(required=True,type='str'),
            dbpath=dict(required=True,type='str'),
            datapath=dict(required=True,type='str')
            )
            ,supports_check_mode=True)
    clean=db2_clean(module)
    clean.parse_params()
    if clean.is_db2_alreadby_installed() == True:
    	  clean.clean_db2()
    #clean.clean_user()
    #clean.clean_group()
    clean.clean_path()
           
    clean.module.exit_json(changed=True, msg="CMD: successed", stdout="", stderr="")

from ansible.module_utils.basic import *
main()

