
# Bug fix to ensure that recaptcha works with google https. It was SSLv2 
# which is considered insecure. Google's server wants to talk only v3. 
# This will force v3. The code is from python bugs site

#http://bugs.python.org/issue11220
# custom HTTPS opener, banner's oracle 10g server supports SSLv3 only
import httplib, ssl, urllib2, socket

class HTTPSConnectionV3(httplib.HTTPSConnection):

    def __init__(self, *args, **kwargs):
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)
        
    def connect(self):
        #print "Trying normal connect"
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        try:
            #print "Doing a v3 connect"
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv3)
        except ssl.SSLError, e:
            #print "Trying v23 instead"
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)
            
class HTTPSHandlerV3(urllib2.HTTPSHandler):
    def https_open(self, req):
        #print "Creating a HTTPS handler"
        return self.do_open(HTTPSConnectionV3, req)

# install opener
#print "INSTALLING CUSTOM HTTPS OPENER"
#urllib2.install_opener(urllib2.build_opener(HTTPSHandlerV3()))

#if __name__ == "__main__":
#    r = urllib2.urlopen("https://ui2web1.apps.uillinois.edu/BANPROD1/bwskfcls.P_GetCrse")
#    print(r.read()) 
