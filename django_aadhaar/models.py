from django.db import models
from django.contrib.auth.models import User 

class Aadhaar(models.Model): 
    # Aadhaar number..
    user    = models.ForeignKey(User, null=True, blank=True)
    aadhaar_id = models.CharField(max_length=12, default="0") 

class AadhaarAuthDetails(models.Model): 
    """
    Store the response results. Extract match bits from the info 
    attribute if necessary. Call pyAadhaarAuth AuthResponse object 
    to extract more details.
    """
    user    = models.ForeignKey(User, null=True, blank=True)
    aadhaar = models.ForeignKey(Aadhaar) 
    ret     = models.CharField(max_length=1, default="n") 
    code    = models.CharField(max_length=40, default="n") 
    err     = models.CharField(max_length=256, default="0") 
    info    = models.CharField(max_length=128, default="") 
    txn     = models.CharField(max_length=128, default="") 
    latency = models.FloatField(default=0) 
    ts      = models.DateTimeField(null=False)

    #=> Store the returned XML 
    _response = models.TextField(
        db_column='response',
        blank=True)        
    def set_response(self, data):
        self._response = data
    def get_response(self):
        return self._response 
    response = property(get_response, set_response)
    
    def get_absolute_url(self):
        return "/aadhaar/txn/%s" % self.txn
    
class AadhaarAuthSummary(models.Model): 
    
    user    = models.ForeignKey(User, null=True, blank=True)
    aadhaar = models.ForeignKey(Aadhaar)
    verified = models.BooleanField(default=False) 
    verification_details = models.ForeignKey(AadhaarAuthDetails, null=True)

    #Time stamps 
    first_authentication = models.DateTimeField(auto_now_add=True) 
    last_unsuccessful_authentication = models.DateTimeField(null=True) 
    last_successful_authentication = models.DateTimeField(null=True) 

    # Stats 
    num_successful_authentications = models.IntegerField(default=0)
    num_unsuccessful_authentications = models.IntegerField(default=0)
    
    def is_valid_aadhaar(self): 
        if (self.aadhaar_id == "0"):
            return False 
        else:
            return True

