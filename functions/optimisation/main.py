#!/usr/bin/env python

from __future__ import print_function


import os
import datetime
import json
import urllib
from subprocess import check_output, Popen
from shutil import copyfile
from tempfile import mkstemp

import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


print('Loading function')

s3 = boto3.client('s3')


target = 'dummy-lambda-test'

OPTIPNG = "bin/optipng"


def optimize(infile, outfile, image_type='png'):
    original = os.path.getsize(infile)
    if image_type in ('jpg', 'jpeg'):
        with open(infile, 'r') as fp:
            original = os.fstat(fp.fileno()).st_size
            print("Image Size: {}".format(original))
            image_bytes = check_output(["bin/jpegoptim", "--strip-all", "-q", "-"], stdin=fp)
            fp.close()

        with open(outfile, 'w') as f:
            f.write(image_bytes)
            optimized = os.fstat(f.fileno()).st_size
            print("Compressed JPG: %s" % format(optimized))
            f.close()
    else:
        os.rename(infile, outfile)
        print("renamed to {}".format(outfile))
        #process = Popen([OPTIPNG, '-quiet', '-o7', outfile])
        process = Popen([OPTIPNG, "-q", "-zc9", "-zm9", "-zs3", "-f0", outfile])
        print("Waiting...")
        process.wait()
        print("PNG optimized")

        optimized = os.path.getsize(outfile)

    return (original, optimized)


def handle(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    now = datetime.datetime.now()

    logger.info("%s - %s", bucket, key)

    try:
        f1, tmp = mkstemp()
        f2, out = mkstemp()

        basename = os.path.basename(key)
        extension = os.path.splitext(basename)[1][1:]
        if extension not in ('png', 'jpeg', 'jpg'):
            return {'message': 'Unauthorized format'}

        response = s3.get_object(Bucket=bucket, Key=key)
        with open(tmp, 'w') as f:
            for chunk in iter(lambda: response['Body'].read(4096), b''):
                f.write(chunk)
        original, optimized = optimize(tmp, out, extension)
        k = s3.head_object(Bucket=bucket, Key=key)
        m = k["Metadata"]
        if "optimized" in m.keys():
            msg = "Image: {} already optimized. Nothing to do".format(key)
            logger.info(msg)
            return {'message': msg}

        metadata = {"original_size": str(original),
                    "compressed_size": "{} [{}%]".format(optimized,
                                                         (optimized / float(original)) * 100.0),
                    "optimized": "True"}

        s3.upload_file(out, target, key, ExtraArgs={"Metadata": metadata, 'ContentType': "image/{}".format(extension)})

        return {'Content-Type': response['ContentType'],
                'Key': key,
                'Bucket': bucket,
                'basename': basename,
                'tmp': tmp
               }
    except Exception as e:
        logger.error(e)
        logger.error('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
        if os.path.isfile(out):
            os.remove(out)
