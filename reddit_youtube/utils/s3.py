import os
import boto3
import toml


# TODO: Client interruption
class S3:

    def __init__(self):
        self.cwd = os.path.dirname(os.path.abspath(__file__))
        self.create_client()

    # TODO: Case for client interruption
    def create_client(self):
        config_file = f"{self.cwd}/../config/config.toml"
        config = toml.load(config_file)["AWS_S3"]
        self.client = boto3.client(
            service_name="s3",
            aws_access_key_id=config["ACCESS_KEY"],
            aws_secret_access_key=config["SECRET_KEY"],
        )

    def s3_path(self, file_name):
        return file_name.replace(f"{self.cwd}/", "")

    def upload(self, local_file):
        if not os.path.isfile(local_file):
            print(f"Local File: {local_file} does not exist")
            return False

        print(f"Uploading {local_file} to s3")
        try:
            response = self.client.upload_file(
                local_file, "spookystories", self.s3_path(local_file)
            )
        except Exception as e:
            print(e)
            return False
        return True

    def download(self, local_file):
        print(f"Downloading {local_file} from s3")
        try:
            self.client.download_file("spookystories", local_file, self.s3_path(
                local_file))
        except Exception as e:
            print(f"s3 File: {local_file} does not exist")
            return False
        return True


    def download_story_audio(self, reddit_id, num_clips):
        print(f"Downloading reddit story: {reddit_id} files from s3")

        if not os.path.exists(reddit_id):
            os.makedirs(reddit_id)

        for clip in range(num_clips):
            if not self.download(f"{reddit_id}/{clip}"):
                return False

        return True

    def delete(self, local_file):
        print(f"Deleting {local_file} from s3.")
        try:
            resp = self.client.delete_object(
                Bucket="spookystories", Key=self.s3_path(local_file)
            )
        except Exception as e:
            print(e)
            return False
        return True

    def files_in_bucket(self, file_path):
        print(f"Getting all file names from s3 with path: {file_path}")
        try:
            response = self.client.list_objects_v2(
                Bucket="spookystories", Prefix=self.s3_path(file_path)
            )
        except Exception as e:
            print(e)
            return set()
        if not "Contents" in response:
            return set()
        return set([f["Key"] for f in response["Contents"]])
