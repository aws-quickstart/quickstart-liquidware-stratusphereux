# This script creates an Amazon Data Lifecycle Management Schedule 

import requests
import boto3
from sys import argv

script, execution_role, target_tag_key, target_tag_value, schedule_name, snapshot_interval, schedule_time, retention = argv

supported_regions = ['us-east-1','us-west-2','eu-west-1']

response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
aws_region = response['region']
print aws_region

def create_dlm_policy(execution_role, target_tag_key, target_tag_value, schedule_name, snapshot_interval, schedule_time, retention):
    dlm_client = boto3.client('dlm', region = aws_region)

    # Creates the Amazon Data Lifecycle Management Schedule for the Workload Specified in the CFN Script
    create_policy = dlm_client.create_lifecycle_policy(
        ExecutionRoleArn = execution_role,
        Description ='string',
        State ='ENABLED',
        PolicyDetails = {
            'ResourceTypes': [
                'VOLUME',
            ],
            'TargetTags': [
                {
                    'Key': target_tag_key,
                    'Value': target_tag_value
                },
            ],
            'Schedules': [
                {
                    'Name': schedule_name,
                    'CreateRule': {
                        'Interval': snapshot_interval,
                        'IntervalUnit': 'HOURS',
                        'Times': [
                            schedule_time,
                        ]
                    },
                    'RetainRule': {
                        'Count': retention
                        }
                },
            ]
        }
    )

if aws_region in supported_regions:
    create_dlm_policy(execution_role, target_tag_key, target_tag_value, schedule_name, snapshot_interval, schedule_time, retention)
else:
    print("DLM not available in Region")