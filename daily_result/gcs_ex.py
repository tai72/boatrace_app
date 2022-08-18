from google.cloud import storage
from tenacity import retry, stop_after_attempt, wait_random
import pandas as pd
import json
from io import BytesIO


class GCSBucket:
    def __init__(self, project_id, bucket):
        client = storage.Client(project_id)
        self.bucket = client.get_bucket(bucket)
        self.project_id = project_id
        

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def list_objects(self, prefix):
        if not prefix.endswith('/'):
            prefix += '/'

        return self.bucket.list_blobs(prefix=prefix)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def list_subdirs(self, prefix):
        if not prefix.endswith('/'):
            prefix += '/'

        blobs = self.bucket.list_blobs(prefix=prefix, delimiter="/")
        subdirs = []

        def strip_prefix(string):
            return string.replace(prefix, "").strip("/")

        for page in blobs.pages:
            subdirs.extend(list(map(strip_prefix, page.prefixes)))

        return subdirs

    def upload_json_from_string(self, string, object_name):
        self.upload_from_string(string, object_name, "application/json")

    def upload_csv_from_string(self, string, object_name):
        self.upload_from_string(string, object_name, "text/csv; charset='utf-8'")

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def upload_from_string(self, string, object_name, content_type="text/plain"):
        blob = self.bucket.blob(object_name)
        blob.upload_from_string(string, content_type=content_type)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def upload_from_file(self, local_filename, object_name):
        blob = self.bucket.blob(object_name)
        blob.upload_from_filename(local_filename)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def read_csv(self, object_name, **kwargs):
        blob = self.bucket.blob(object_name)
        content = blob.download_as_string()
        return pd.read_csv(BytesIO(content), **kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def read_json(self, object_name):
        blob = self.bucket.blob(object_name)
        content = blob.download_as_string()
        return json.loads(content)

    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def read_model(self, object_name):
        blob = self.bucket.blob(object_name)
        content = blob.download_as_string().decode()
        return content

    def check_blob_exists(self, path: str) -> bool:
        return self.bucket.blob(path).exists()
