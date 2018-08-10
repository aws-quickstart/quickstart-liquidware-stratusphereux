# This script creates an Amazon Data Lifecycle Management Schedule 

import boto3

dlm_client = boto3.client('dlm')

def lambda_handler(event, context):
    execution_role = event['ResourceProperties']['ExecutionRole']
    target_tag_key = event['ResourceProperties']['TargetTags']['Key']
    target_tag_value = event['ResourceProperties']['TargetTags']['Value']
    retention = event['ResourceProperties']['Retention']
    snapshot_interval = event['ResourceProperties']['ScheduleInterval']
    schedule_time = event['ResourceProperties']['ScheduleTime']
    schedule_name = event['ResourceProperties']['ScheduleName']

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