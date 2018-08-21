# This lambda function creates an Amazon Data Lifecycle Management Schedule 
# from a Cloudformation Custom Resource

import boto3

dlm_client = boto3.client('dlm')

def lambda_handler(event, context):
    from botocore.vendored import requests
    import json
    
    non_supported_regions = ['ap-northeast-3','eu-west-3']

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    NONSUPPORTED = "DLM not available in Region"

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
    def create_dlm_policy(event):
        execution_role = event['ResourceProperties']['ExecutionRole']
        target_tag_key = event['ResourceProperties']['TargetTags']['Key']
        target_tag_value = event['ResourceProperties']['TargetTags']['Value']
        retention = event['ResourceProperties']['Retention']
        snapshot_interval = event['ResourceProperties']['ScheduleInterval']
        schedule_time = event['ResourceProperties']['ScheduleTime']
        aws_region = event['ResourceProperties']['AWSRegion']

        create_policy = dlm_client.create_lifecycle_policy(
            ExecutionRoleArn = execution_role,
            Description ='DLM Schedule Created for {} by Quick Start'.format(target_tag_value),
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
                        'Name': '{} DLM Schedule'.format(target_tag_value),
                        'CreateRule': {
                            'Interval': int(snapshot_interval),
                            'IntervalUnit': 'HOURS',
                            'Times': [
                                schedule_time,
                            ]
                        },
                        'RetainRule': {
                            'Count': int(retention)
                            }
                    },
                ]
            }
        )
        send(event, context, SUCCESS, create_policy)
    
    if aws_region not in non_supported_regions:
        try:
            create_dlm_policy(execution_role, target_tag_key, )
        except Exception as exc:
            send(event, context, FAILED , exc)
    else:
        send(event, context, FAILED, NONSUPPORTED)