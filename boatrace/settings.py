import os
import json
import environ
from pathlib import Path
print('s')


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env file
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if os.getenv('GAE_APPLICATION', None):
    # 本番環境
    DEBUG = False
else:
    # 開発環境
    DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'daily_result.apps.DailyResultConfig',
    'authentication.apps.AuthenticationConfig', 

    'django.contrib.sites',     # django-allauthが内部で使えるようにするため
    'allauth', 
    'allauth.account', 
    'allauth.socialaccount', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boatrace.urls'

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

WSGI_APPLICATION = 'boatrace.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# sqlite3での設定
if os.environ.get('GAE_APPLICATION', None):
    # 本番環境（CloudSQL）
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql', 
    #         'NAME': env('DB_NAME'), 
    #         'USER': env('DB_USER'), 
    #         'PASSWORD': env('DB_PASSWORD'), 
    #         'HOST': '/cloudsql/{}'.format(env('INSTANCE_CONNECTION_NAME')), 
    #     }
    # }
    # 本番環境（PostgreSQL）
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', 
            'NAME': env('DB_NAME_DEV'), 
            'USER': env('DB_USER_DEV'), 
            'PASSWORD': env('DB_PASSWORD_DEV'), 
            'HOST': '', 
            'PORT': '', 
        }
    }
else:
    # 開発環境（PostgreSQL）
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', 
            'NAME': env('DB_NAME_DEV'), 
            'USER': env('DB_USER_DEV'), 
            'PASSWORD': env('DB_PASSWORD_DEV'), 
            'HOST': '', 
            'PORT': '', 
        }
    }
# else:
#     # 開発環境（Cloud SQL）
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql', 
#             'NAME': env('DB_NAME'), 
#             'USER': env('DB_USER'), 
#             'PASSWORD': env('DB_PASSWORD'), 
#             'HOST': '127.0.0.1', 
#             'PORT': '3306', 
#         }
#     }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ロギング設定
LOGGING = {
    'version': 1, 
    'disable_existing_loggers': False, 

    # ロガーの設定
    'loggers': {
        # Djangoが利用するロガー
        'django': {
            'handlers': ['console'], 
            'level': 'INFO', 
        },
        # daily_resultアプリケーションが利用するロガー
        'daily_result': {
            'handlers': ['console'], 
            'level': 'DEBUG', 
        },
    },

    # ハンドラの設定
    'handlers': {
        'console': {
            'level': 'DEBUG', 
            'class': 'logging.StreamHandler', 
            'formatter': 'dev',
        },
    },

    # フォーマッタの設定
    'formatters': {
        'dev': {
            'format': '\t'.join([
                '%(asctime)s', 
                '[%(levelname)s]', 
                '%(pathname)s(Line:%(lineno)d)',
                '%(message)s',
            ])
        },
    }
}

# 静的ファイルのパス設定
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'), 
)

# メールの配信先をコンソールにする設定
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# メールサーバー設定
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASS')
EMAIL_USE_TLS = True

# カスタムユーザーモデルを参照するようにするため
AUTH_USER_MODEL = 'authentication.CustomUser'

# django-allauthで利用するdjango.contrib.sitesを使うためにサイト識別用IDを設定
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',     # 一般ユーザー用（メールアドレス認証）
    'django.contrib.auth.backends.ModelBackend',               # 管理サイト用（ユーザー名認証）
)

# メールアドレス認証に変更する設定
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

# サインアップにメールアドレス確認設定をはさむよう設定
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True

# ログイン / ログアウト後の遷移先を設定
LOGIN_REDIRECT_URL = 'daily_result:index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'account_login'

# ログアウトリンクのクリック一発でログアウトする設定
ACCOUNT_LOGOUT_ON_GET = True

# django-allauthが送信するメールの件名自動付与される接頭辞をブランクにする設定
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

# デフォルトのメール送信元を設定
DEFAULT_FROM_EMAIL = env('EMAIL_HOST')
