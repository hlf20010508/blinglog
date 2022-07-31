import minio
from flask import _app_ctx_stack


class Minio(object):
    """This class is used to control the Minio integration to one or more Flask
    applications.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
        self.client = None

    def init_app(self, app):
        app.config.setdefault('MINIO_ENDPOINT', 'play.minio.io:9000')
        app.config.setdefault('MINIO_ACCESS_KEY', 'Q3AM3UQ867SPQQA43P2F')
        app.config.setdefault('MINIO_SECRET_KEY',
                              'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG')
        app.config.setdefault('MINIO_SECURE', True)
        app.config.setdefault('MINIO_REGION', None)
        app.config.setdefault('MINIO_HTTP_CLIENT', None)
        app.teardown_appcontext(self.teardown)

        self.client = self.init_minio(app.config)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['minio'] = self.client

    def init_minio(self, config):
        return minio.Minio(
            config.get('MINIO_ENDPOINT'),
            access_key=config.get('MINIO_ACCESS_KEY'),
            secret_key=config.get('MINIO_SECRET_KEY'),
            secure=config.get('MINIO_SECURE'),
            region=config.get('MINIO_REGION'),
            http_client=config.get('MINIO_HTTP_CLIENT')
        )

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'minio'):
            ctx.minio._http.clear()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'minio'):
                ctx.minio = self.client
            return ctx.minio

    def put_object(self, bucket_name, object_name, data, length,
                   content_type="application/octet-stream",
                   metadata=None, sse=None, progress=None,
                   part_size=0, num_parallel_uploads=3,
                   tags=None, retention=None, legal_hold=False):
        return self.client.put_object(bucket_name, object_name, data, length,
                               content_type, metadata, sse, progress,
                               part_size, num_parallel_uploads,
                               tags, retention, legal_hold)

    def remove_object(self, bucket_name, object_name, version_id=None):
        self.client.remove_object(bucket_name, object_name, version_id)

    def list_objects(self, bucket_name, prefix=None, recursive=False,
                     start_after=None, include_user_meta=False,
                     include_version=False, use_api_v1=False,
                     use_url_encoding_type=True):
        return self.client.list_objects(bucket_name, prefix, recursive,
                                 start_after, include_user_meta,
                                 include_version, use_api_v1,
                                 use_url_encoding_type)

    def bucket_exists(self, bucket_name):
        return self.client.bucket_exists(bucket_name)

    def make_bucket(self, bucket_name, location=None, object_lock=False):
        self.client.make_bucket(bucket_name, location, object_lock)

    def set_bucket_policy(self, bucket_name, policy):
        self.client.set_bucket_policy(bucket_name, policy)