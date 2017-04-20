#!/usr/bin/env python

from __future__ import print_function

import sys
import os
import argparse

try:
    import boto3
except ImportError:
   print('Please install boto3 to use this tool')
   sys.exit(1)

profile_name=os.environ.get('profile_name')
boto3.setup_default_session(profile_name=profile_name, region_name='eu-west-1')

def main(bucket, lambdas, events):

    data = {}
    data['LambdaFunctionConfigurations'] = [
                {
                    'LambdaFunctionArn': _lambda,
                    'Events': events
                }
                for _lambda in lambdas if _lambda
            ]
    print(data)
    s3 = boto3.resource('s3')
    bucket_notification = s3.BucketNotification(bucket)
    try:
        response = bucket_notification.put(NotificationConfiguration=data)
        print('Bucket notification updated successfully')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Manage S3 bucket notifications')
    parser.add_argument('--bucket', dest='bucket', required=True,
                        help='the S3 bucket name')
    parser.add_argument('--lambda', dest='lambdas', nargs='*',
                        help='Lambda ARN')
    parser.add_argument('--event', dest='events', nargs='*',
                        default=['s3:ObjectCreated:*'],
                        help='an event to respond to')
    args = parser.parse_args()

    main(args.bucket, args.lambdas, args.events)
