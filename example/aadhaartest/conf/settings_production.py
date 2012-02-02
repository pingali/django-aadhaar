import os, sys
import logging 
from django import templatetags 
from .settings_local import * 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEPLOYMENT_TYPE="PRODUCTION"
DEPLOYMENT_SERVER="aadhaartest.com"
DEPLOYMENT_DIR="/home/ubuntu/workspace/aadhaartest"

def findglobalpath(path):
    return os.path.abspath(os.path.join(DEPLOYMENT_DIR,path))

#sys.path.insert(0, "/home/ubuntu/aadhaar/django-auth-aadhaar")

HTTP_PREFIX="http://"
logfile=findglobalpath('logs/aadhaartest.django.log')
database=findglobalpath('shared/aadhaartest.sqlite.db')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': database,
        'USER': '',      
        'PASSWORD': '',  
        'HOST': '',      
        'PORT': '',      
    }
}

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s',
                    filename=logfile, 
                    filemode='a+',
                    handlers=[handler],
                    )

