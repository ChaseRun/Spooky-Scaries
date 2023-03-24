import os

import boto3
import toml


def s3_path(file_name):
    cwd = os.path.dirname(os.path.abspath(__file__))
    return file_name.replace(f"{cwd}/", "")


def s3_client():
    cwd = os.path.dirname(os.path.abspath(__file__))
    config_file = f"{cwd}/../config/config.toml"
    config = toml.load(config_file)["AWS_S3"]
    return boto3.client(
        service_name="s3",
        aws_access_key_id=config["ACCESS_KEY"],
        aws_secret_access_key=config["SECRET_KEY"],
    )


def upload(local_file):
    if not os.path.isfile(local_file):
        print(f"Local File: {local_file} does not exist")
        return False

    print(f"Uploading {local_file} to s3")
    client = s3_client()
    try:
        response = client.upload_file(
            local_file, "spookystories", s3_path(local_file)
        )
    except Exception as e:
        print(e)
        return False
    return True


def download(local_file):
    print(f"Downloading {local_file} from s3")
    client = s3_client()
    try:
        client.download_file("spookystories", local_file, s3_path(local_file))
    except Exception as e:
        print(f"s3 File: {local_file} does not exist")
        return False
    return True


def delete(local_file):
    print(f"Deleting {local_file} from s3.")
    client = s3_client()
    try:
        resp = client.delete_object(
            Bucket="spookystories", Key=s3_path(local_file)
        )
    except Exception as e:
        print(e)
        return False
    return True


def files_in_bucket(file_path):
    print(f"Getting all file names from s3 with path: {file_path}")
    client = s3_client()
    try:
        response = client.list_objects_v2(
            Bucket="spookystories", Prefix=s3_path(file_path)
        )
    except Exception as e:
        print(e)
        return set()
    if not "Contents" in response:
        return set()
    return set([f["Key"] for f in response["Contents"]])
