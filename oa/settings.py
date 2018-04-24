# -*- coding: utf-8 -*-
"""
Django settings for oa project.

Generated by 'django-login startproject' using Django 1.8.18.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Buioa paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7ijgn#r_#nqy+!yclvmzu9)h985t!5awck4)wjnnzk6eixzqf+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login',
    'no_attendance',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'oa.urls'

#全局变量  css js img
#CSS_PATH=

#html模板位置定义
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #html模板位置定义
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #全局变量引用 上下文处理
                'login.views.global_setting',
            ],
        },
    },
]

WSGI_APPLICATION = 'oa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'oa',
        'USER': 'crontab',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
        'HOST': '192.168.50.226',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

#自定义css、js静态文件访问路径
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),

)


#网站的基本信息配置，setting全局变量
# SITE_TITLE = '零度后台管理'
# #页面url
# SITE_LOGIN = '/login/'
# SITE_OUT = '/logout/'
# SITE_PASSWD = '/passwd'
# SITE_HOME = '/ver/index' #主页
# SITE_SUBMIT = '/ver/submit/'
# SITE_UPDATE = '/ver/update/'
# SITE_ROLLBACK = '/ver/rollback/'
# SITE_RESTART = '/ver/service_restart/'
SITE_URL = 'http://192.168.50.226:888/no_attendance/todo/'

# SITE_ENTER = 0 #进度条初始值
