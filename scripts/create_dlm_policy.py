# This lambda function creates an Amazon Data Lifecycle Management Schedule 
# from a Cloudformation Custom Resource

import boto3

dlm_client = boto3.client('dlm')

def lambda_handler(event, context):
    from botocore.vendored import requests
    import json
    
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    
    execution_role = event['ResourceProperties']['ExecutionRole']
    target_tag_key = event['ResourceProperties']['TargetTags']['Key']
    target_tag_value = event['ResourceProperties']['TargetTags']['Value']
    retention = event['ResourceProperties']['Retention']
    snapshot_interval = event['ResourceProperties']['ScheduleInterval']
    schedule_time = event['ResourceProperties']['ScheduleTime']
    schedule_name = event['ResourceProperties']['ScheduleName']

    # This function helps generate the response back to the CFN Custom Resource
    def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
        responseUrl = event['ResponseURL']

        print(responseUrl)

        responseBody = {}
        responseBody['Status'] = responseStatus
        responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
        responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
        responseBody['StackId'] = event['StackId']
        responseBody['RequestId'] = event['RequestId']
        responseBody['LogicalResourceId'] = event['LogicalResourceId']
        responseBody['NoEcho'] = noEcho
        responseBody['Data'] = responseData

        json_responseBody = json.dumps(responseBody)

        print("Response body:\n" + json_responseBody)

        headers = {
            'content-type' : '',
            'content-length' : str(len(json_responseBody))
        }

        try:
            response = requests.put(responseUrl,
                                    data=json_responseBody,
                                    headers=headers)
            print("Status code: " + response.reason)
        except Exception as e:
            print("send(..) failed executing requests.put(..): " + str(e))
    
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
    
    send(event, context, SUCCESS, create_policy)