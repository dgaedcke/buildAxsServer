# DB settings
HOST = '127.0.0.1'
PORT = '3306'
USER = 'payApp'
PW = 'apple1010'
DB_NAME = 'pay'
DB_ECHO = False

# FILE system.
PATH_PREFIX = '/opt/paysys/'
PATH_WWW_DIR = PATH_PREFIX + 'www/'
PATH_SOURCE_DIR = PATH_PREFIX + 'current/source/'
PATH_JOB_DIR = PATH_SOURCE_DIR + 'jobs/'
PATH_LOG_DIR = PATH_PREFIX + 'logs/'
PATH_FTP_DIR = PATH_PREFIX + 'ftp/'
PATH_UPLOAD_DIR = PATH_SOURCE_DIR + 'web/uploads/'
PATH_RULE_GEN_DIR = PATH_PREFIX + 'rules/'

# CELERY.
TIMEZONE = 'America/Denver'
SEND_TASK_ERROR_EMAILS = True
SKIP_ASYNC_INFRASTRUCTURE = False

# Top email is the default for job notification if no email is specified.
ADMINS = [
    ('Dewey Gaedcke', 'dewey@pathoz.com'),
    ('Andy Lasada', 'Alasda@examiner.com'),
    ('Marc Ingram', 'mIngram@examiner.com')
]

# EMAIL.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USER = 'dewey@minggl.com'
EMAIL_PW = 'LUARIBBIT'
EMAIL_PORT = '465'
EMAIL_USE_SSL = True

MAIL_CONFIG = {'host': EMAIL_HOST, 'un': EMAIL_USER, 'pw': EMAIL_PW, 'port': EMAIL_PORT, 'use_ssl': EMAIL_USE_SSL}

# FLASK / WEB.
WEB_HOST_DOMAIN = 'localhost'
WEB_HOST_PORT = ':5000'

# Used to generate the download URL for files in job-notification emails.
_host_template = 'http://%s%s'
WEB_HOST = _host_template % (WEB_HOST_DOMAIN, WEB_HOST_PORT)

_file_dl_template = _host_template + '/files/'
DL_URL_PREFIX = _file_dl_template % (WEB_HOST_DOMAIN, WEB_HOST_PORT)

FLASK_DEBUG = True
WEB_SECRET_KEY = 'broohaha123'

# RABBIT-MQ.
BROKER_URL = 'amqp://'

# JOB SERVER.
RENAME_COMPLETED_FILES = True
