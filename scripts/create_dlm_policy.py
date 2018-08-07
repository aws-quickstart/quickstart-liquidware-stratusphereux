import boto3

dlm_client = boto3.client('dlm')

def lambda_handler(event, context):
    
    create_policy = dlm_client.create_lifecycle_policy(
        ExecutionRoleArn='string',
        Description='string',
        State='ENABLED',
        PolicyDetails={
            'ResourceTypes': [
                'VOLUME',
            ],
            'TargetTags': [
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            'Schedules': [
                {
                    'Name': 'string',
                    'TagsToAdd': [
                        {
                            'Key': 'string',
                            'Value': 'string'
                        },
                    ],
                    'CreateRule': {
                        'Interval': 24,
                        'IntervalUnit': 'HOURS',
                        'Times': [
                            '00:00',
                        ]
                    },
                    'RetainRule': {
                        'Count': 7
                        }
                },
            ]
        }
    )
