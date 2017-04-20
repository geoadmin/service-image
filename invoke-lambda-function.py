#!/usr/bin/env python


from __future__ import print_function
import json
import boto3
import botocore
import sys
import argparse


# https://github.com/cleesmith/boto3_test


def convertStreamingBody(obj):
    if isinstance(obj, botocore.response.StreamingBody):
        return obj.__str__()


def main(function_name, fname, profile='default'):

    with open(fname, 'r') as f:
        data = f.read()
        payload = json.loads(data)

    print(function_name)
    print(payload)
    boto3.setup_default_session(profile_name='borghi', region_name='eu-west-1')

    client = boto3.client('lambda', region_name='eu-west-1')
    r = client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',  # 'Event',
        #Payload=b'fileb://{}'.format(fname) #json.dumps(payload)
        LogType='Tail',
        Payload=json.dumps(payload)
    )

    print(json.dumps(r, indent=4, default=convertStreamingBody))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("function", help="AWS Lambda function name")

    parser.add_argument("event", help="Event file name")
    parser.add_argument("--profile", help="AWS account profile")
    args = parser.parse_args()

    main(args.function, args.event, profile=args.profile)
