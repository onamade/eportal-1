from .base import *

DEBUG = False
ADMINS = [(
    ('Peter B', 'shell.appointment@gmail.com'),
)]

ALLOWED_HOSTS = ['*']
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'eportal',
#         'USER': 'eportal',
#         'PASSWORD': os.environ['PASSWORD'],
#         'HOST': os.environ['HOST'],
#         'PORT': os.environ['PORT'],
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
