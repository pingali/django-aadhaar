import os, sys
import logging 
from settings_local import * 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DEPLOYMENT_DIR=findpath(".")
def findglobalpath(path):
    return os.path.abspath(os.path.join(DEPLOYMENT_DIR,path))

sys.path.insert(0, findpath("../../django-auth-aadhaar"))

HTTP_PREFIX="http://"
DEPLOYMENT_TYPE="DEVELOPMENT"
DEPLOYMENT_SERVER="localhost:8000"
database=findpath('aadhaartest.sqlite.db')
logfile=findpath('aadhaartest.django.log')
print DEPLOYMENT_TYPE

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
                    #filename=logfile, 
                    #filemode='a+',
                    handlers=[handler],
                    )

