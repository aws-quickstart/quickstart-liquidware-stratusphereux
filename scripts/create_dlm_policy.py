# This script creates an Amazon Data Lifecycle Management Schedule 

import requests, json, argparse, boto3

supported_regions = ['us-east-1','us-west-2','eu-west-1']

url = 'http://169.254.169.254/latest/dynamic/instance-identity/document'

try:
    r = requests.get(url).content
    aws_region = json.loads(r)['region']
except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)

#aws_region = json.loads(requests.get(url).content)['region']

def create_dlm_policy(args):
    dlm_client = boto3.client('dlm',region_name = aws_region)

    # Creates the Amazon Data Lifecycle Management Schedule for the Workload Specified in the CFN Script
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("execution-role", help = "Specify the AWS ARN of the Role DLM schedule will utilize")
    parser.add_argument("target_tag_key", help = "Specify the Tag Key that DLM will target, i.e TagKey = TagValue")
    parser.add_argument("target_tag_value", help = "Specify the Tag Value that DLM will target. i.e TagKey = TagValue")
    parser.add_argument("snapshot_interval", help = "Specify the Interval hours between snapshots, 12 and 24 are the only valid options", type=int)
    parser.add_argument("schedule_time", help = "The DLM Schedule will start within one hour of the specified time")
    parser.add_argument("retention", help = "The # of snapshots that will be retained, if a snapshot is taken daily and this is set to 7 it will keep 7 Days worth of snapshots", type=int)
    args = parser.parse_args()

    if aws_region in supported_regions:
        try:
            create_dlm_policy(args)
        except Exception as exc:
            print("Error creating policy:", exc)
    else:
        print("DLM not available in Region")
