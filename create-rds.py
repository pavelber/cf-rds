import json
import os
import random
import subprocess
import sys

stack_name =  sys.argv[1]

params = {
  'DBInstanceID': 'test7',
  'DBName': 'test',
  'DBInstanceClass':'db.m5.large',
  'DBAllocatedStorage': '50',
  'OpenPortInSecurityGroup': '5432',
  'DBUsername': 'bezos',
  'DBPassword': 'rApt0REnge1ne',
  'DBSubnetId1':'subnet-0718a13efae7851c6',
  'DBSubnetId2':'subnet-0dfed541b118772ef',
  'VPCId': 'vpc-0467db844c9d7bdf8',
  'CidrForDbAccess': '10.50.0.0/16'
}

params_line = ['ParameterKey=%s,ParameterValue=%s' % (key, value) for (key, value) in params.items()]


execute_params = ['aws', 'cloudformation', 'create-stack', '--stack-name', stack_name, '--template-body',
                  'file://create-rds.yml','--parameters'] + params_line

print("Starting aws stack creation\n")
print(execute_params)

create_stack  = subprocess.run(execute_params)

if create_stack.returncode != 0:
    print("Stack creation failed.\n")
    exit(1)


while True:
    describe_params = ['aws', 'cloudformation', 'describe-stacks', '--stack-name', stack_name] 
    describe = subprocess.run(describe_params, capture_output=True, text=True)
    status_json =  json.loads(describe.stdout)
    status = status_json["Stacks"][0]["StackStatus"]
    print("Status "+status+"\n")
    if status == 'CREATE_COMPLETE':
        print("Stack created\n")
        break
    if status in ['CREATE_FAILED','ROLLBACK_COMPLETE']:
        print("Stack failed\n")
        events_params = ['aws', 'cloudformation', 'describe-stack-events', '--stack-name', stack_name] 
        subprocess.run(events_params)
        exit(1)
        


