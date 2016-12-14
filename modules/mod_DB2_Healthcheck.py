#!/usr/bin/python
from __future__ import division
import os
import json
import datetime


class db2hc:
  def __init__(self, module):
      self.module = module
        
  def run_command(self,cmd):
        rc,stdout,stderr=module.run_command(cmd,use_unsafe_shell=True)
        if stderr != '' or rc !=0:
            self.module.fail_json(changed=False, msg="CMD: %s Failure" % cmd,stderr=stderr, rc=rc, stdout = stdout)   
        return stdout
  	    	   
     
  def col_runing_instance(self):
  	    cmd="ps -ef|grep -i db2sysc|grep -v grep|awk '{print $1}'"
  	    stdout=self.run_command(cmd)
  	    instance=stdout.strip('\n').strip().split('\n')
            if instance[0] == '':
                instance=[]
  	    return instance
  	    
  def col_os_info(self):
  	   cmd="uname -s"
  	   stdout=self.run_command(cmd)
  	   osinfo=stdout.strip('\n').strip()
  	   return osinfo
  
  def col_all_version(self):
  	   osinfo=self.col_os_info()
  	   if osinfo  == 'Linux' and os.path.exists("/opt/ibm/db2"):
  	   	  cmd="ls /opt/ibm/db2/"
  	   	  stdout=self.run_command(cmd)
  	   	  all_version=stdout.strip('\n').strip().split('\n')
  	   elif osinfo  == 'AIX' and os.path.exists("/opt/IBM/db2"):
  	   	  cmd="ls /opt/IBM/db2/"
  	   	  stdout=self.run_command(cmd)
  	   	  all_version=stdout.strip('\n').strip().split('\n')
  	   else:
  	   	  all_version=[]  	   	  
  	   return all_version
  	  
  def col_all_instance(self):
  	   versions=self.col_all_version()
  	   osinfo=self.col_os_info()
  	   all_instance=[]
  	   if len(versions) !=0 and osinfo == 'Linux':
  	   	   for v in versions:
  	   	   	   cmd="/opt/ibm/db2/"+v+"/instance/db2ilist"
  	   	   	   stdout=self.run_command(cmd)
  	   	   	   all_instance.extend(stdout.strip('\n').strip().split('\n'))
  	   elif len(versions) !=0 and osinfo == 'AIX':
  	   	   for v in versions:
  	   	   	   cmd="/opt/IBM/db2/"+v+"/instance/db2ilist"
  	   	   	   stdout=self.run_command(cmd)
  	   	   	   all_instance.extend(stdout.strip('\n').strip().split('\n'))
	   return all_instance
        
  def col_level(self,inst):
  	   cmd="su - " + inst  + " -c 'db2level'|grep -i 'Informational'|awk -F'\"' '{print $2}'|awk '{print $2}'"
  	   level=self.run_command(cmd).strip('\n')
  	   cmd="su - " + inst  + " -c 'db2level'|grep -i 'Product'|awk -F'\"' '{print $2}'"
  	   path=self.run_command(cmd).strip('\n')
  	   cmd="su - "+inst+" -c 'db2level'"
  	   stdout=self.run_command(cmd)
  	   header="=============== db2 level info==============="
  	   self.col_writefile(header,stdout) 
  	   return (level,path)
  	  
  def col_writefile(self,header,message):
  	  file_path='/tmp/db2check'
  	  if not os.path.exists(file_path):
  	  		os.mkdir(file_path)
  	  now=datetime.datetime.now()
  	  timestamp=now.strftime('%Y%m%d')
  	  filename='db2hc_detail.out'
  	  files=os.path.join(file_path,filename)
  	  f=open(files,'a')
  	  f.write(header)
  	  f.write('\n')
  	  f.write(message)
  	  f.write('\n')
  	  f.close()
  	  
  	 
       
  def col_database(self,inst):
  	   cmd="su - " + inst + " -c 'db2 list db directory'|grep -i 'Database name'|awk -F'=' '{print $2}'"
  	   stdout=self.run_command(cmd)
  	   database=stdout.strip('\n').strip().split('\n')    
  	   return database
  	  
  def col_system(self):
          osinfo=self.col_os_info()
          if osinfo == 'Linux':
  	     cmd="cat /proc/meminfo|grep 'MemTotal'|awk -F' ' '{print $2}'"
  	     stdout=self.run_command(cmd)
  	     MEM=stdout.strip('\n').strip()
  	     MEM_GB=int(round(int(MEM)/1024/1024))
  	     MEM_B=MEM_GB*1024*1024*1024
  	     SHMMNI=str(256*MEM_GB)
  	     SHMMAX=str(MEM_B)
  	     SHMALL=str(MEM_B*2)
  	     SEMMNI=str(256*MEM_GB)
  	     MSGMNI=str(1024*MEM_GB)
  	     SEM='250\t25600\t32\t'+str(SEMMNI)

  	     std_kernel={'shmmni':SHMMNI,'shmmax':SHMMAX,'shmall':SHMALL,'sem':SEM,'msgmni':MSGMNI,'msgmax':'65536','msgmnb':'65536'}
  	     for k,v in std_kernel.items():	
  	  	cmd="sysctl -a|grep -w "+k+" |awk -F'=' '{print $2}'"
  	  	stdout=self.run_command(cmd)
  	  	cur_v=stdout.strip('\n').strip()
  	  	std_kernel[k]=[cur_v,v]	   
          else:
            std_kernel={'shmmni':['auto','auto'],'shmmax':['auto','auto'],'shmall':['auto','auto'],'sem':['auto','auto'],'msgmni':['auto','auto'],
'msgmax':['auto','auto'],'msgmnb':['auto','auto']}
  	  return std_kernel
	


  def col_param(self,inst,db):
           param=['LOCKTIMEOUT','LOCKLIST','MAXLOCKS','SOFTMAX','LOGFILSIZ','LOGPRIMARY','LOGSECOND','LOGARCHMETH1']
           json_param={}
          
           for i in param: 
             cmd="su - " + inst + " -c 'db2 get db cfg for  "+ db +"\'|grep -w " + i +"|awk -F'=' '{print $2}'"
             stdout=self.run_command(cmd)
             value=stdout.strip('\n').strip()
             json_param[i]=value 
           if  json_param['LOGARCHMETH1'] == 'OFF':
           	  res="RECYCLE"
           else:
           	  res="ARCHIVE"
           cmd="su - "+inst+" -c 'db2 get db cfg for "+db+"'"
           stdout=self.run_command(cmd)
           header="===============db2 database info ==============="
           self.col_writefile(header,stdout)
           return res
           
  def col_tablespace(self,inst,db):
     cmd="su - " + inst + " -c 'db2 connect to   "+ db +" >/dev/null;db2 -x select tbspace from syscat.tablespaces;db2 terminate >/dev/null'"
     stdout=self.run_command(cmd)
     tablespace=stdout.strip('\n').replace('\n',',').replace(' ','').split(',')
     tbsp_param={'tbsp_type':'TBSP_TYPE','tbsp_state':'TBSP_STATE','tbsp_autostorage':'TBSP_USING_AUTO_STORAGE','tbsp_autoresize':'TBSP_AUTO_RESIZE_ENABLED','tbsp_utilization':'TBSP_UTILIZATION_PERCENT'}
     
     tablespace_dict={}
     status_flag=0
     perecent_flag=0
     for tbsp in tablespace: 
         json_tbsp_param={}
         for key,param in tbsp_param.items():
              cmd='su - '+inst+' -c \"db2 connect to '+db+'>/dev/null;db2 -x \\"select '+param+' from sysibmadm.MON_TBSP_UTILIZATION where TBSP_NAME=\''+tbsp+'\'\\";db2 terminate>/dev/null\"'
              stdout=self.run_command(cmd)
              value=stdout.strip('\n').strip()
              json_tbsp_param[key]=value
         
         if json_tbsp_param['tbsp_type']=='DMS' and json_tbsp_param['tbsp_autoresize']=='0' and json_tbsp_param['tbsp_autostorage']=='0' and json_tbsp_param['tbsp_utilization'] > '80':
         	  perecent_flag +=1
         if json_tbsp_param['tbsp_state'] != 'NORMAL':
            status_flag +=1
     
     if perecent_flag !=0:
     	  tablespace_dict['percent']="WARNING"
     else:
     	  tablespace_dict['percent']="GOOD"
     	  
     if status_flag !=0:
     	  tablespace_dict['status']="ERROR"
     else:
     	  tablespace_dict['status']="GOOD"
     
     cmd='su - '+inst+' -c " db2 connect to '+db+'>/dev/null;db2pd -d  '+db+' -tab;db2 terminate >/dev/null"'
     stdout=self.run_command(cmd)
     header="===============db2 tablespace info==============="
     self.col_writefile(header,stdout)   
     return tablespace_dict   
         
  def col_snapdb(self,inst,db):
        snapdb_param={"snap_status":"DB_STATUS","snap_location":"DB_LOCATION","snap_backup":"LAST_BACKUP" ,"snap_connection":"CONNECTIONS_TOP","snap_deadlock":"DEADLOCKS" ,"snap_lockescal":"LOCK_ESCALS" ,"snap_locktimeout":"LOCK_TIMEOUTS","snap_total_sorts":"TOTAL_SORTS" ,"snap_sort_overflow":"SORT_OVERFLOWS"}
        snapdb_dict={}
        
        for key,param in snapdb_param.items():
             cmd="su - "+inst+" -c 'db2 connect to "+db+">/dev/null;db2 -x select "+param+" from sysibmadm.snapdb;db2 terminate>/dev/null'"
             stdout=self.run_command(cmd)
             value=stdout.strip('\n').strip()
             snapdb_dict[key]=value
        if snapdb_dict["snap_status"] != "ACTIVE":
        	  snapdb_dict["snap_status"]="ERROR"
        else:
        	 snapdb_dict["snap_status"]="GOOD" 
        if snapdb_dict["snap_deadlock"] !='0':
            snapdb_dict["snap_deadlock"]="WARNING"
        else:
        	  snapdb_dict["snap_deadlock"]="GOOD"
        if snapdb_dict["snap_lockescal"] !='0':
            snapdb_dict["snap_lockescal"]="WARNING"
        else:
        	  snapdb_dict["snap_lockescal"]="GOOD"
        if snapdb_dict["snap_locktimeout"] !='0':
            snapdb_dict["snap_locktimeout"]="WARNING"
        else:
        	  snapdb_dict["snap_locktimeout"]="GOOD"
        if snapdb_dict["snap_total_sorts"] != '0':
            sort_overflow_percent=round(int(snapdb_dict["snap_sort_overflow"])/int(snapdb_dict["snap_total_sorts"])*100)	
        else:
        	  sort_overflow_percent=0
        if sort_overflow_percent <=3:
        	  snapdb_dict['sort_overflow_percent']="GOOD"
        else:
        	  snapdb_dict['sort_overflow_percent']="WARNING" 
         
        return snapdb_dict
         
         
  def col_bufferpool(self,inst,db):
       
     cmd="su - " + inst + " -c 'db2 connect to   "+ db +" >/dev/null;db2 -x select bpname from syscat.bufferpools;db2 terminate >/dev/null'"
     stdout=self.run_command(cmd)
     bufferpool=stdout.strip('\n').replace('\n',',').replace(' ','').split(',')
   
     buff_param={'data_hit_ratio':'DATA_HIT_RATIO_PERCENT','index_hit_ratio':'INDEX_HIT_RATIO_PERCENT'}
     json_buff_param={}
     bufferpool_dict={}
     hitratio_flag=0
     
     for buff in bufferpool: 
         json_buff_param={}
         for key,param in buff_param.items():
              cmd='su - '+inst+' -c \"db2 connect to '+ db +'>/dev/null;db2 -x \\"select '+param+' from sysibmadm.MON_BP_UTILIZATION where BP_NAME=\''+buff+'\'\\";db2 terminate>/dev/null\"'
              stdout=self.run_command(cmd)
              value=stdout.strip('\n').strip()
              json_buff_param[key]=value        
         
         if json_buff_param['data_hit_ratio'] < '85':
         	  hitratio_flag +=1

     if hitratio_flag !=0:
        bufferpool_dict['hitratio']="WARNING"   
     else:
     	  bufferpool_dict['hitratio']="GOOD"  
     cmd='su - '+inst+' -c " db2 connect to '+db+'>/dev/null;db2pd -d  '+db+' -buff;db2 terminate >/dev/null"'
     stdout=self.run_command(cmd)
     header="===============db2 bufferpool info==============="
     self.col_writefile(header,stdout) 
     return bufferpool_dict
  
def main():
    global module
    overall_status=0
    module = AnsibleModule(argument_spec = dict(),supports_check_mode=True)
    db=db2hc(module)
    instance=db.col_runing_instance()
    all_instance=db.col_all_instance()
    
    json_dict={}
    json_dict['db2']={"instance":{}}
    inst_list=[]
    if len(all_instance) != 0:
     for i in all_instance:
       json_inst_dict={i:{}}
       if i not in instance:
         json_inst_dict[i]=0
         header="===============check instnace "+i+" start==============="
         res="not runing"
         db.col_writefile(header,res)
       else:
         cmd="su - "+i+" -c 'db2 get dbm cfg '"
         stdout=db.run_command(cmd)
         header="===============check instnace "+i+" start==============="
         db.col_writefile(header,stdout)
         cmd="su - "+i+" -c 'db2set -all'" 
         stdout=db.run_command(cmd)
         header="===============db2set paramter==============="
         db.col_writefile(header,stdout)
         cmd="su - "+i+" -c 'db2 list db directory'" 
         stdout=db.run_command(cmd)
         header="=============== database info ==============="
         db.col_writefile(header,stdout)
         level,path=db.col_level(i)
         json_inst_dict[i]={'level':level}
       
         dbs=db.col_database(i)
         db_list=[]
         for d in dbs:
            cmd='su - '+i+' -c " db2 connect to '+d+'>/dev/null;db2 get snapshot for db on '+d+';db2 terminate >/dev/null"'
            stdout=db.run_command(cmd)
            header="===============db2 database snapshot ==============="
            db.col_writefile(header,stdout)        	   
       	    json_db_dict={'db':{}}
       	    json_db_dict['level']=level
       	    json_db_dict['path']=path
            param_value=db.col_param(i,d)
            json_db_dict['db']['LOGMETHOD']=param_value
            json_db_dict['db']['dbName']=str(d)
            tablespace=db.col_tablespace(i,d)
            json_db_dict['db']['tablespace']=tablespace
            bufferpool=db.col_bufferpool(i,d)
            json_db_dict['db']['bufferpool']=bufferpool
            snap=db.col_snapdb(i,d)
            json_db_dict['db']['status']=snap['snap_status']
            json_db_dict['db']['connections']=snap['snap_connection']
            json_db_dict['db']['lastbackup']=snap['snap_backup']
            json_db_dict['db']['deadlock']=snap['snap_deadlock']
            json_db_dict['db']['lockeasl']=snap['snap_lockescal']
            json_db_dict['db']['locktimeout']=snap['snap_locktimeout']
            json_db_dict['db']['sortoverflow']=snap['sort_overflow_percent']
            db_list.append(json_db_dict)
         json_inst_dict[i]=db_list
       inst_list.append(json_inst_dict)
     json_dict['db2']['instance']=inst_list

     json_dict['db2']["System Paramters"]=db.col_system()
    
           
     json_str=json.dumps(json_dict) 
     if 'ERROR' in json_str:
   	     json_dict['overall']=2
     elif 'WARNING' in json_str:
    	     json_dict['overall']=1
     else:
    	    json_dict['overall']=0
    else:
      json_dict['db2']['instance']=[]
      json_dict['overall']=-1
        
    jsonstr=json.dumps(json_dict)
    db.module.exit_json(changed=True, msg="CMD: successed", stdout=jsonstr, stderr="")

from ansible.module_utils.basic import *
main()
