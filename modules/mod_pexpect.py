#!/usr/bin/env python
#coding:utf-8

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: my_sample_module

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    ip:
        description:
            - This is the message to send to the sample module
        required: true
    command:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import pexpect
import pdb

def ssh_cmd(ip, command):
    SECURITY_HOST = '192.168.1.11'
    SECURITY_USERNAME = 'root'
    SECURITY_PASSWORD = 'passw0rd'

    ssh = pexpect.spawn('ssh %s@%s' % (SECURITY_USERNAME, SECURITY_HOST))
    try:
        ret = ssh.expect(['[P|p]assword:', 'continue connecting (yes/no)?'], timeout=15) 
        if ret == 0:
            ssh.sendline(SECURITY_PASSWORD)
        elif ret == 1:
            ssh.sendline('yes')
            ssh.expect('[P|p]assword:')
            ssh.sendline(SECURITY_PASSWORD) 

        '''
        ssh.expect('SAG>')
        ssh.sendline('/'+ip)
        ssh.expect('SAG>')
        ssh.sendline('2')
        ssh.expect('#')
        ssh.sendline(command)  
        ssh.expect('#')
        '''
        
        ssh.expect('SAG>')
        ssh.sendline('1')
        ssh.expect('SAG>')
        
        retStr = ssh.before
        search_Num = re.search(r'([0-9]+):AIX-'+ip, retStr, re.I)
        ip_Num = search_Num.group(1)
        
        ssh.sendline(ip_Num)
        ssh.expect('#')
        ssh.sendline(command)  
        ssh.expect('#')
        
    except pexpect.EOF:
       print "EOF"
    except pexpect.TIMEOUT:
       print "TIMEOUT"
    finally:
       ssh.close() 

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        ip = dict(type='str', required=True),
        command = dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_message'] = module.params['ip']
    result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params['ip']:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['command'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)
    
    ssh_cmd(module.params['ip'], module.params['command'])
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
