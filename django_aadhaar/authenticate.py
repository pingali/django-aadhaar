import os, sys 
from django.db import models
from django.conf import settings 
from django.contrib.auth import backends
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import User, AnonymousUser
from config import Config
from datetime import datetime 
import logging 
import traceback 
import gc 
import simplejson as json 
from django import forms
from django_auth_aadhaar.forms import AadhaarAuthForm 
from django.contrib import messages
from models import Aadhaar, AadhaarAuthSummary, AadhaarAuthDetails
import dateutil.parser 

from AadhaarAuth.request import AuthRequest
from AadhaarAuth.data import AuthData
from AadhaarAuth.command import AuthConfig 
from AadhaarAuth.response import AuthResponse


log = logging.getLogger("apps.aadhaar.authenticate") 


#=================================================================
# Prevent sql commands from being printed out for this section...
from django.db.backends import BaseDatabaseWrapper
from django.db.backends.util import CursorWrapper

if settings.DEBUG:
    BaseDatabaseWrapper.make_debug_cursor = \
        lambda self, cursor: CursorWrapper(cursor, self)
#==================================================================

class AadhaarHelper(object): 
    
    _user = None 
    _credentials = {}
    
    def __init__(self): 
        if not hasattr(settings, "AADHAAR_SETTINGS"): 
            setattr(settings, 'AADHAAR_SETTINGS', AadhaarSettings())
            if not settings.AADHAAR_SETTINGS.is_valid(): 
                raise Exception("Configuration file is invalid") 
            
    def get_credentials(self): 
        log.debug("authenticate: Returning credentials = %s " % self._credentials)
        return self._credentials 

    def process_credentials(self, cfg, credentials): 
        
        log.debug("process_credentials: received credentials %s " % credentials) 

        # Process the credentials now....
        #<Pid ts= ver=>
        #  <Meta fdc= idc= apc=>
        #     <Locn lat= lng= vtc= subdist= dist= state= pc=/>
        #  </Meta>
        #  <Demo lang=>
        #  <Pi ms=E|P mv= name= lname= lmv= gender=M|F|T dob= dobt=V|D|A age= phone= email=/>
        #   <Pa ms=E co= house= street= lm= loc= vtc= 
        #            subdist= dist= state= pc= po=/>
        #  <Pfa ms=E|P mv= av= lav= lmv=/>
        # </Demo>
        # <Bios>
        #   <Bio type=FMR|FIR|IIR pos=>encoded biometric</Bio>
        # </Bios>
        # <Pv otp= pin=/>
        # </Pid>
        
        attribute_hash = { 
            'aadhaar_pi_match': ("Pi", "ms"),
            'aadhaar_name':     ("Pi", "name"),
            'aadhaar_dob':      ("Pi", "dob"),
            'aadhaar_gender':   ("Pi", "gender"),
            'aadhaar_email':    ("Pi", "email"),
            'aadhaar_phone':    ("Pi", "phone"),
            'aadhaar_pa_match':  ("Pa", "ms"),
            'aadhaar_co':       ("Pa", "co"),
            'aadhaar_house':    ("Pa", "house"),
            'aadhaar_street':   ("Pa", "street"), 
            'aadhaar_landmark': ("Pa", "lm"), 
            'aadhaar_locality': ("Pa", "loc"), 
            'aadhaar_vtc':      ("Pa", "vtc"),
            'aadhaar_subdist':  ("Pa", "subdist"),
            'aadhaar_district': ("Pa", "dist"),
            'aadhaar_state':    ("Pa", "state"),
            'aadhaar_pincode':  ("Pa", "pc"),
            'aadhaar_postoffice': ("Pa", "po"),
            }

        #{ u'aadhaar_district': [u''], u'aadhaar_match': [u'E'],
        #u'aadhaar_subdist': [u''], u'aadhaar_vtc': [u''],
        #u'aadhaar_name': [u''], u'aadhaar_email':
        #[u'sdfdsf@gnai.com'], u'next': [u'/'], u'aadhaar_attributes':
        #[u'aadhaar_gender', u'aadhaar_co'], u'aadhaar_postoffice':
        #[u''], u'csrfmiddlewaretoken':
        #[u'7f1f3b29e69001d329dec6f335ce9f35'], u'aadhaar_street':
        #[u''], u'aadhaar_locality': [u''], u'aadhaar_gender': [u'M'],
        #u'aadhaar_house': [u''], u'aadhaar_co': [u''],
        #u'aadhaar_landmark': [u''], u'aadhaar_state': [u''],
        #u'aadhaar_phone': [u''], u'aadhaar_dob': [u''],
        #u'aadhaar_pincode': [u''], u'aadhaar_id': [u'123412341234']}>
        
        config_hash = {} 
        selected_attributes = credentials ['aadhaar_attributes']
        if len(selected_attributes) == 0: 
            raise forms.ValidationError("Select one or more authentication parameters") 
        for attribute in selected_attributes:
            if not attribute_hash.has_key(attribute): 
                log.error("Missing attribute: %s" % attribute)
                raise forms.ValidationError("Unknown attribute '%s' specified" % attribute)
            # This attribute is being used. So save it. 
            self._credentials[attribute]  = credentials[attribute] 

            xml_attr_set = attribute_hash[attribute][0]
            xml_attr_name = attribute_hash[attribute][1] # as per the protocol

            humanized_attribute = AadhaarAuthForm.humanize(attribute) 
            if not credentials.has_key(attribute):
                raise forms.ValidationError("Field '%s' is missing" % humanized_attribute)
            xml_attr_value = credentials[attribute]
            
            if not config_hash.has_key(xml_attr_set): 
                config_hash[xml_attr_set] = {} 
                
            config_hash[xml_attr_set][xml_attr_name] = xml_attr_value 
        
        cfg.request.biometrics = [] 
        for xml_attr_set in ["Pi", "Pa"]: 
            if (config_hash.has_key(xml_attr_set) and 
                not config_hash[xml_attr_set].has_key("ms")):
                raise forms.ValidationError("PII/address Matching strategy "+
                                            " must be specified")
            if config_hash.has_key(xml_attr_set): 
                cfg.request[xml_attr_set] = config_hash[xml_attr_set]
                cfg.request['demographics'] = config_hash.keys() 
        
        log.debug("request to server = %s " % cfg.request )
        return cfg
    
    def get_aadhaar(self):

        log.debug("get_aadhaar()") 

        # Create the aadhaar object and save it in the profile 
        aadhaar = None
        aadhaar_id = self._aadhaar_id
        request = self._request 
        if (not request.user.is_anonymous()): 
            try: 
                profile = request.user.get_profile() 
                aadhaar = profile.aadhaar 
                if (aadhaar == None): 
                    (aadhaar,created) = \
                        Aadhaar.objects.get_or_create(aadhaar_id=aadhaar_id,
                                                      user=request.user)
            except: 
                log.exception("authentcate:get_aadhaar()")
                pass 
        else:
            # Anonymous user. Make note of this aadhaar request. This
            # is a valid UID and user data 
            (aadhaar,created) = \
                Aadhaar.objects.get_or_create(aadhaar_id=self._aadhaar_id)

        if (aadhaar == None): 
            raise Exception("Could not retrieve/create aadhaar object") 

        return aadhaar 

    def authenticate(self, request, cleaned_data): 
        """
        Eventually support all possible combinations and levels 
        of authentication 
        """
        # Store this object...
        self._request = request 

        if ((cleaned_data == None) or 
            (not isinstance(cleaned_data, dict))):
            raise Exception("Invalid data to authenticate")

        # cleanup and extract the aadhaar
        credentials = {} 
        for k,v in cleaned_data.iteritems():
            if k.startswith('aadhaar'):
                if k not in ["aadhaar_dob", "aadhaar_pincode"]: 
                    credentials[k] = v
                else: 
                    credentials[k] = str(v)  # authdata requires a string...

        log.debug("authenticate: storing credentials = %s " % credentials)

        aadhaar_settings = settings.AADHAAR_SETTINGS 
        if ((aadhaar_settings == None) and (not aadhaar_settings.is_valid())):
            raise Exception("Aadhaar configuration unspecified or invalid") 

        try: 
            self._aadhaar_id = credentials['aadhaar_id']
        except: 
            raise Exception("UID not specified")
        
        cfg = aadhaar_settings.get_cfg() 
        #print("cfg = %s " % cfg)

        # Issue the request 
        cfg.request.uid = self._aadhaar_id 
        self.process_credentials(cfg, credentials) 

        print("request  %s " % cfg.request)

        # => Generate the request XML and send it over the 
        # server 
        try: 
            data = AuthData(cfg=cfg) 
            data.generate_client_xml() 
            exported_data = data.export_request_data() 
            
            log.debug("Completed PidXML generation")
            log.debug("Requesting connection with UIDAI backend")

            req = AuthRequest(cfg)
            log.debug("Created authrequest object")            
            req.import_request_data(exported_data)
            req.execute()

            log.debug("Completed  authrequest. Processing response")

            # Load the response 
            data = json.loads(req.export_response_data())
            res = AuthResponse(cfg=cfg, uid=cfg.request.uid) 
            res.load_string(data['xml'])
            
            log.debug("Completed processing response") 
        
            # Find all the attributes set 
            bits = res.lookup_usage_bits()
            log.debug("[%.3f] (%s) -> %s " % (data['latency'], bits, data['ret']))
            if data['err'] is not None and data['err'] != -1: 
                log.debug("Err %s: %s "% ( data['err'], data['err_message']))
        except: 
            # For whatever the authentication failed. 
            log.debug("Exception in the call to pyAadhaarAuth library")
            traceback.print_exc() 
            log.exception("authenticate: call failed for some reason")  
            raise Exception("Authentication call failed. Internal error")
        
        try: 
            aadhaar = self.get_aadhaar() 
        except: 
            log.exception("authencate: get_aadhaar failed")

        log.debug("aadhaar object created/obtained %s " % vars(aadhaar))
                
        # Create a new AuthDetails record 
        latency = data['latency'] 
        ts = dateutil.parser.parse(unicode(data['ts']))
        authdetails = AadhaarAuthDetails(
            aadhaar=aadhaar,
            ret = data['ret'],
            latency = round(latency, 2),
            err = data['err'], 
            ts = ts, 
            txn = data['txn'],
            info = data['info'],
            code = data['code'], 
            )
        authdetails.set_response(data['xml'])
        if (not request.user.is_anonymous()):
            authdetails.user = request.user
        authdetails.save() 
        
        log.debug("authdetails object = %s " % vars(authdetails))

        if (not request.user.is_anonymous()):
            # Create an auth aummary for a given aadhaar id
            (authsummary, created) = \
                AadhaarAuthSummary.objects.get_or_create(aadhaar=aadhaar, 
                                                         user=request.user)

            # XXX Change this. May be we should rename this as last
            # verification details. 
            authsummary.verification_details=authdetails
            authsummary.verified = req.is_successful()
            if (created): 
                authsummary.first_authentication = datetime.now()
            if (req.is_successful()): 
                log.debug("Successful authentication. So updating state")
                authsummary.last_successful_authentication = datetime.now() 
                authsummary.num_successful_authentications += 1 
            else:
                log.debug("Unsuccessful authentication. So updating state")
                authsummary.last_unsuccessful_authentication = datetime.now() 
                authsummary.num_unsuccessful_authentications += 1             
            authsummary.save() 
            self._authsummary = authsummary 
            log.debug("auth summary created/updated %s " % vars(authsummary))
        
        if ((req.is_successful()) and (not request.user.is_anonymous())):
            log.debug("Successful auth. Saving aadhaar in the profile")
            profile = request.user.get_profile() 
            profile.aadhaar = aadhaar
            profile.save() 

        return (req.is_successful(), authdetails) 
    
class AadhaarSettings(object):
    """
    This is a simple class to take the place of the global settings object. A
    instance will contain all of our settings as attributes, with default val
    if they are not specified by the configuration.
    """
    def __init__(self, cfg_file=None):
        """
        Loads our settings from django.conf.settings, applying defaults for a
        that are omitted.
        """
        if (cfg_file is None):
            if hasattr(settings, 'AADHAAR_CONFIG_FILE'):
                cfg_file = settings.AADHAAR_CONFIG_FILE
            
        if cfg_file == None or not (os.path.isfile(cfg_file)): 
            raise Exception("AADHAAR_CONFIG_FILE is either undefined or does not exist") 
        
        # Load it up...
        c = AuthConfig(cfg=cfg_file)
        self.cfg = c.update_config()
        
    def get_cfg(self): 
        return self.cfg 

    def is_valid(self): 
        # Validate the configuration file to make sure 
        # the components are 
        if hasattr(self, 'cfg') and self.cfg is not None: 
            return True 
        else:
            return False 



