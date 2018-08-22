# This lambda function creates an Amazon Data Lifecycle Management Schedule 
# from a Cloudformation Custom Resource

def lambda_handler(event, context):
    import json, boto3
    from botocore.vendored import requests

    non_supported_regions = ['ap-northeast-3','eu-west-3']
    aws_region = event['ResourceProperties']['AWSRegion']
    req_type = event['RequestType']
    dlm_client = boto3.client('dlm')
    
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
    
    
    # Creates the Amazon Data Lifecycle Management Schedule for the workload specified in the CFN Script
    def create_dlm_policy(event):
        execution_role = event['ResourceProperties']['ExecutionRole']
        target_tag_key = event['ResourceProperties']['TargetTags']['Key']
        target_tag_value = event['ResourceProperties']['TargetTags']['Value']
        retention = event['ResourceProperties']['Retention']
        snapshot_interval = event['ResourceProperties']['ScheduleInterval']
        schedule_time = event['ResourceProperties']['ScheduleTime']

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
        print(create_policy)
        send(event, context, SUCCESS, create_policy, create_policy['PolicyId'])
    
    # Deletes the Amazon Data Lifecycle Management Schedule for the workload specified in the CFN Script
    def delete_dlm_policy(event):
        policy_id = event['PhysicalResourceId']

        delete_policy = dlm_client.delete_lifecycle_policy(
            PolicyId = event['PhysicalResourceId']
            )
        print(delete_policy)
        send(event, context, SUCCESS, delete_policy)

    # Updates the Amazon Data Lifecycle Management Schedule for the workload specified in the CFN Script
    def update_dlm_policy(event):
        policy_id = event['PhysicalResourceId']
        execution_role = event['ResourceProperties']['ExecutionRole']
        target_tag_key = event['ResourceProperties']['TargetTags']['Key']
        target_tag_value = event['ResourceProperties']['TargetTags']['Value']
        retention = event['ResourceProperties']['Retention']
        snapshot_interval = event['ResourceProperties']['ScheduleInterval']
        schedule_time = event['ResourceProperties']['ScheduleTime']
        policy_state = event['ResourceProperties']['PolicyState']

        update_policy = dlm_client.update_lifecycle_policy(
            PolicyId= policy_id,
            ExecutionRoleArn = execution_role,
            State = policy_state,
            Description='DLM Schedule Updated for {} by Quick Start'.format(target_tag_value),
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
        print(update_policy)
        send(event, context, SUCCESS, update_policy, policy_id)
        
    actions = {
        'Create': create_dlm_policy,
        'Delete': delete_dlm_policy,
        'Update': update_dlm_policy
    }

    try:
        if aws_region in non_supported_regions:
            print(NONSUPPORTED)
            send(event, context, SUCCESS, NONSUPPORTED)
        else:
            actions.get(req_type)(event)    
    except Exception as exc:
        error_msg = {'Error': exc}
        print(error_msg)
        send(event, context, FAILED, error_msg)