import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5kqvq=cm4s$6!^dth*8xm7w191#6ds^9n8^%h7si&e9yl0)w!1'
SECRET_KEY = os.getenv('SECRET_KEY', SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  # os.environ.get('SERVER_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '.herokuapp.com', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'app',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

# Allow Cross Origin Access for local Angular App
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost',
    'http://localhost:4200',
    'http://localhost:8080',
    'http://localhost:8081',
    'https://localhost:8443',
    'https://example.firebaseapp.com',
]

ROOT_URLCONF = 'mechanics_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mechanics_api.wsgi.application'

# Rest framework
REST_FRAMEWORK = {'EXCEPTION_HANDLER': 'app.utils.handlers.custom_exception_handler'}

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'mechanics'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'root'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

# Azure
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')

# SMTP
EMAIL_HOST = os.environ.get('SMTP_HOST')
EMAIL_PORT = os.environ.get('SMTP_PORT', 25)
EMAIL_USE_TLS = os.environ.get('SMTP_SECURE', False)
EMAIL_HOST_USER = os.environ.get('SMTP_USERNAME', '')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
EMAIL_FROM = os.environ.get('SMTP_EMAIL_FROM')

GENERAL_INVITATION_URL = os.environ.get('GENERAL_INVITATION_URL', 'https://example.firebaseapp.com')
WORKSPACE_INVITATION_URL = os.environ.get(
    'WORKSPACE_INVITATION_URL',
    'https://example.firebaseapp.com/accept-invitation?token=<token>',
)

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(name)s: %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
            'default_msec_format': '%03d',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'
