lambda-image
============

AWS Lambda function to optimise small OGC WMTS tiles (png and jpeg) in agiven AWS S3 bucket.


# Installation

The management of the AWS Lambda function is done with [apex](https://github.com/apex/apex).
Please read [apex.run](http://apex.run/) for background infos on this utility.

Initialise environmetal variables for you project/AWS account:

  $ source config

Dowload `apex` and generate configuration files:

  $ make all

Deploy your function:

  $ make deploy

Add the notification to you S3 bucket:

  $ make put_bucket_notification

