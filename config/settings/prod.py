import dj_database_url
from decouple import Csv
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403,F401


def required_config(name):
    value = config(name, default="").strip()
    if not value:
        raise ImproperlyConfigured(f"{name} is required for production settings.")
    return value


def required_csv_config(name):
    values = config(name, default="", cast=Csv())
    if not values:
        raise ImproperlyConfigured(f"{name} must contain at least one value in production.")
    return values


DEBUG = False
SECRET_KEY = required_config("SECRET_KEY")
ALLOWED_HOSTS = required_csv_config("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = required_csv_config("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = required_csv_config("CSRF_TRUSTED_ORIGINS")

DATABASES = {
    "default": dj_database_url.parse(
        required_config("DATABASE_URL"),
        conn_max_age=60,
        ssl_require=True,
    )
}

INSTALLED_APPS += ["storages"]

AWS_ACCESS_KEY_ID = required_config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = required_config("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = required_config("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = required_config("AWS_S3_REGION_NAME")
AWS_S3_ENDPOINT_URL = required_config("AWS_S3_ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN", default="").strip()
AWS_DEFAULT_ACL = "private"
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

default_storage_options = {
    "access_key": AWS_ACCESS_KEY_ID,
    "secret_key": AWS_SECRET_ACCESS_KEY,
    "bucket_name": AWS_STORAGE_BUCKET_NAME,
    "region_name": AWS_S3_REGION_NAME,
    "endpoint_url": AWS_S3_ENDPOINT_URL,
    "default_acl": AWS_DEFAULT_ACL,
    "querystring_auth": AWS_QUERYSTRING_AUTH,
    "file_overwrite": AWS_S3_FILE_OVERWRITE,
}

if AWS_S3_CUSTOM_DOMAIN:
    default_storage_options["custom_domain"] = AWS_S3_CUSTOM_DOMAIN

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": default_storage_options,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = (
    f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    if AWS_S3_CUSTOM_DOMAIN
    else f"{AWS_S3_ENDPOINT_URL.rstrip('/')}/{AWS_STORAGE_BUCKET_NAME}/"
)

SECURE_SSL_REDIRECT = env_flag("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_flag(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
SECURE_HSTS_PRELOAD = env_flag("SECURE_HSTS_PRELOAD", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
