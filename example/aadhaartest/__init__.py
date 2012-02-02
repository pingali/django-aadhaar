
# Bug fix to ensure that recaptcha works with google https. It was SSLv2 
# which is considered insecure. Google's server wants to talk only v3. 
# This will force v3. The code is from python bugs site

import urllib2 
from .lib.connection import HTTPSHandlerV3 

# install opener
#print "INSTALLING CUSTOM HTTPS OPENER"
urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))

#if __name__ == "__main__":
#    r = urllib2.urlopen("https://ui2web1.apps.uillinois.edu/BANPROD1/bwskfcls.P_GetCrse")
#    print(r.read()) 
