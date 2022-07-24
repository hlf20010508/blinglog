# :project: bluelog
# :author: L-ING
# :copyright: (C) 2022 L-ING <hlf01@icloud.com>
# :license: MIT, see LICENSE for more details.

from minio import Minio
from minio.error import S3Error
import config as myconfig

config = myconfig.load()
port = config['host_minio'].split(':')[1]
host = '127.0.0.1:%s' % port if config['local_minio'] else config['host_minio']
username = config['username_minio']
password = config['password_minio']
bucket = config['bucket']
secure = config['secure_minio']


class Client:
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    def __init__(self, host=host, username=username, password=password, bucket=bucket, secure=secure):
        self.client = Minio(
            host,
            access_key=username,
            secret_key=password,
            secure=secure
        )
        # for printing
        self.host = host
        self.bucket = bucket

    def upload(self, remote_path, data):
        try:
            self.client.put_object(
                self.bucket, remote_path, data, -1, part_size=5*1024*1024)
            print(
                "file is successfully uploaded as \n object %s to bucket %s." % (
                    remote_path, self.bucket)
            )
            address = 'http://'+config['host_minio'] + \
                '/'+self.bucket+'/'+remote_path
            print(address)
            return address
        except S3Error as exc:
            print("error occurred.", exc)

    def remove(self, remote_path):
        try:
            self.client.remove_object(self.bucket, remote_path)
            print("%s is successfully removed from bucket %s" %
                  (remote_path, self.bucket))
        except S3Error as exc:
            print("error occurred.", exc)

    def list(self):
        try:
            obj_list = self.client.list_objects(self.bucket, recursive=True)
            obj_list = [obj.object_name for obj in obj_list]
            return obj_list
        except S3Error as exc:
            print("error occurred.", exc)
