from django.db import models
from django.contrib.auth.models import User 
from django.db.models.signals import post_save 
import simplejson as json 
from django_auth_aadhaar.forms import AadhaarAuthForm 
from django_aadhaar.models import Aadhaar 
from django.contrib import messages 
import logging

log = logging.getLogger("apps.account.models")

class UserProfile(models.Model): 

    user = models.ForeignKey(User, unique=True)    
    aadhaar = models.ForeignKey(Aadhaar, blank=True, null=True) 

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        log.debug("Adding user profile for %s " % instance.username)
        p = UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
