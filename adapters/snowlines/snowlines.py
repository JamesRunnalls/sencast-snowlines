#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" This adapter gets the snow-ice from a Polymer file """

import os
import sys
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# key of the params section for this adapter
PARAMS_SECTION = "SNOWLINES"

# the file name pattern for output file
FILENAME = "L2SNOW_{}"
FILEFOLDER = "L2SNOW"
# The name of the xml file for gpt
GPT_XML_FILENAME = "snowlines_OLCI.xml"


def apply(env, params, l2product_files, date):
    """Apply Snowlines adapter.
        1. Calculates Snowlines from IdePix output

        Parameters
        -------------

        params
            Dictionary of parameters, loaded from input file
        env
            Dictionary of environment parameters, loaded from input file
        l2product_files
            Dictionary of Level 2 product files created by processors
        date
            Run date
        """
    print("Applying Snowline...")

    gpt = env['General']['gpt_path']

    # Check for IDEPIX precursor dataset
    if "IDEPIX" not in l2product_files or not os.path.exists(l2product_files["IDEPIX"]):
        raise RuntimeWarning("IDEPIX precursor file not found ensure IDEPIX is run before this adapter.")

    # Create folder for file
    product_path = l2product_files["IDEPIX"]
    product_name = os.path.basename(product_path)
    product_dir = os.path.join(os.path.dirname(os.path.dirname(product_path)), FILEFOLDER)
    output_file = os.path.join(product_dir, FILENAME.format(product_name))

    if os.path.isfile(output_file):
        if "synchronise" in params["General"].keys() and params['General']['synchronise'] == "false":
            print("Removing file: ${}".format(output_file))
            os.remove(output_file)
        else:
            print("Skipping Snowline, target already exists: {}".format(FILENAME.format(product_name)))
            upload_to_s3(output_file, "snowlines-satellite", os.path.basename(output_file),
                         env['SNOWLINES']['aws_access'],
                         env['SNOWLINES']['aws_secret'])
            return output_file
    os.makedirs(product_dir, exist_ok=True)

    gpt_xml_file = os.path.join(product_dir, "_reproducibility", GPT_XML_FILENAME)
    rewrite_xml(gpt_xml_file, product_path, output_file)

    args = [gpt, gpt_xml_file, "-c", env['General']['gpt_cache_size']]
    if subprocess.call(args):
        if os.path.exists(output_file):
            os.remove(output_file)
        else:
            print("No file was created.")
        raise RuntimeError("GPT Failed.")

    upload_to_s3(output_file, "snowlines-satellite", os.path.basename(output_file), env['SNOWLINES']["aws_access"],
                  env['SNOWLINES']["aws_secret"])


def rewrite_xml(gpt_xml_file, input_file, output_file):
    with open(os.path.join(os.path.dirname(__file__), GPT_XML_FILENAME), "r") as f:
        xml = f.read()

    xml = xml.replace("${infile}", input_file)
    xml = xml.replace("${outfile}", output_file)
    os.makedirs(os.path.dirname(gpt_xml_file), exist_ok=True)
    with open(gpt_xml_file, "w") as f:
        f.write(xml)


def upload_to_s3(local_file, bucket, s3_file, access_key, secret_key):
    print("Uploading output to S3 Bucket...")
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    if exists_in_s3(s3, bucket, s3_file):
        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            raise RuntimeError("Failed to find input file to upload to S3 bucket")
        except NoCredentialsError:
            print("Credentials not available")
            raise RuntimeError("Credentials not available to upload to S3 bucket")


def exists_in_s3(s3, bucket, s3_file):
    try:
        s3.head_object(Bucket=bucket, Key=s3_file)
        print("File already exists in S3")
        return False
    except ClientError as e:
        return True
    return True
