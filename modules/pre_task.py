#!/usr/bin/python

from fabric.api import *
from os import path

env.abort_on_prompts = True
os_type = 'Linux'
local_ssh_pub = '/root/.ssh/id_rsa.pub'
local_ssh_pri = '/root/.ssh/id_rsa'

def local_task():
    if path.isfile(local_ssh_pub) and path.isfile(local_ssh_pri):
       pass
    else:
       local('ssh-keygen -t rsa -b 4096')

def add_key():
    global os_type
	if os_type == "Linux":
	   remote_ssh_pub = '/root/.ssh/id_rsa.pub'
       remote_ssh_aut = '/root/.ssh/authorized_keys'
	else:
	   env.shell = '/usr/bin/ksh'
	   remote_ssh_pub = '/.ssh/id_rsa.pub'
       remote_ssh_aut = '/.ssh/authorized_keys' 
    with settings(warn_only=True):
        local_pub_str = local('cat %s' % local_ssh_pub, capture=True)
        remote_aut_str = run('cat %s' % remote_ssh_aut, pty=False)
        if local_pub_str not in remote_aut_str: 
           put(local_ssh_pub, remote_ssh_pub)
           run('cat %s >> %s' % (remote_ssh_pub, remote_ssh_aut), pty=False)
			
def check_python():
     global os_type
     with settings(warn_only=True):
         os_type = run('uname', pty=False)
         if os_type.find('ksh') != -1:
		    env.shell = '/usr/bin/ksh'
            if_python = run('which python', pty=False)
            if "no python" in if_python:
               run('mkdir -p /tmp/itoatools', pty=False)
               put('/opt/tornado/tools/aixtools.python.2.7.12.2.I', '/tmp/itoatools')
               run('installp -acgXYd /tmp/itoatools aixtools.python.rte 2.7.12.2 aixtools.python.man.en_US 2.7.12.2', pty=False)
			   run('ln -s /opt/bin/python /usr/bin/python', pty=False)
		   
def check_others():
    with settings(warn_only=True):
        if_unzip = run('which unzip', pty=False)
        if "no unzip" in if_unzip:
           run('rpm -ivh /tmp/itoatools/unzip-6.0-3.aix6.1.ppc.rpm', pty=False)

def put_files():
    run('mkdir -p /tmp/itoatools', pty=False)
    put('/opt/tornado/tools/unzip-6.0-3.aix6.1.ppc.rpm', '/tmp/itoatools')

@task
def add_box():
    execute(check_python)
	execute(local_task)
    execute(add_key)
	
@task
def install_requisite():
    execute(put_files)
    execute(check_others)
