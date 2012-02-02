# Bug fix to ensure that recaptcha works with google https. It was SSLv2 
# which is considered insecure. Google's server wants to talk only v3. 
# This will force v3. The code is from python bugs site

#import urllib2 
#from aadhaartest.lib.connection import HTTPSHandlerV3 
#
# install opener
#print "INSTALLING CUSTOM HTTPS OPENER"
#urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))
