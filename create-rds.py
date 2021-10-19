import json
import os
import subprocess
import sys

stack_name =  sys.argv[1]

params = {
  'DBEngine': 'postgres',
  'DBEngineVersion': '12.3',
  'DBInstanceID': 'test1',
  'DBName': 'test',
  'DBInstanceClass':'db.m5.large',
  'DBAllocatedStorage': '50',
  'OpenPortInSecurityGroup': '5432',
  'DBUsername': 'bezos',
  'DBPassword': 'rApt0REnge1ne',
  'DBSubnetId1':'subnet-0d9688833b0d01280',
  'DBSubnetId2':'subnet-06ef17562f044ed15',
  'VPCId': 'vpc-014df93204c1a2f59',
  'CidrForDbAccess': '10.50.0.0/16',
  'KeyName':'xxxx',
  'PublicSubnetId':'subnet-0d9688833b0d01280',
  'RestoreRoleArn': ''
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
        endpoint = status_json["Stacks"][0]["Outputs"][0]["OutputValue"] # If you have more than one output, check OutputKey to be "Endpoint"
        break
    if status in ['CREATE_FAILED','ROLLBACK_COMPLETE']:
        print("Stack failed\n")
        events_params = ['aws', 'cloudformation', 'describe-stack-events', '--stack-name', stack_name] 
        subprocess.run(events_params)
        exit(1)
        
my_env = os.environ.copy()
my_env["PGPASSWORD"] = params["DBPassword"]
query_params = ['psql','-h',endpoint,'-U',params["DBUsername"],params["DBName"]]
p = subprocess.Popen(query_params, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)    
grep_stdout = p.communicate(input=b'select 1;')[0]
print(grep_stdout.decode())
        


