#-*- coding: utf-8 -*-
from django import forms
from django.conf import settings 
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import AadhaarLoginForm
import simplejson as json
from .authenticate import AadhaarHelper 
from models import AadhaarAuthDetails, AadhaarAuthSummary, Aadhaar 
import logging
import traceback 

log = logging.getLogger("aadhaar.views")

@login_required 
def authenticate(request, detail):
    
    user = request.user 

    if detail not in ["personal", "address", "all"]:
        messages.error(request,"Unknown type of authentication")
        return HttpResponseRedirect("/")     

    session = request.session 

    if request.method == "POST":
        log.debug("received post %s " % request.POST )

        form = AadhaarLoginForm(detail=detail, data=request.POST)
        if form.is_valid():
            try: 
                helper = AadhaarHelper() 
                (result, authdetail) = helper.authenticate(request, form.cleaned_data)
                
                if ((result == True) and (request.user.is_authenticated())): 
                    log.debug("Valid authentication.")
                    
                if result is False:
                    messages.error(request, "Authentication Failed. Please doublecheck all the inputs")                    
            except: 
                messages.error(request, "Internal error. We are looking into it")
                result = False 
                traceback.print_exc() 
                log.exception("authenticate call") 

            if result is True:
                messages.success(request, ("You have been successfully authenticated (txn: <a href='%s'>%s</a>) !" % (authdetail.get_absolute_url(), authdetail.txn)))
                if request.POST.get('next'):
                    next = form.cleaned_data['next'] 
                else:
                    next = "/"
                return HttpResponseRedirect(next) 


       # they are covered anyway
       # else:
            #messages.error(request, form.errors)

    else:
        # Support redirect
        initial = {} 
        state = None
        if request.GET.get('next') != None: 
            next = request.GET.get('next')
        else:
            next = "/"
        initial['next'] = next 
        form = AadhaarLoginForm(detail=detail, initial=initial)
            
    template = {"form":form}
    return render_to_response(
        'aadhaar/authenticate.html', 
        template, 
        RequestContext(request))
 
@login_required 
def txn(request,txn_id): 
    log.debug("txn: txn_id = %s " % txn_id)
    try: 
        detail = AadhaarAuthDetails.objects.get(txn=txn_id)
    except: 
        traceback.print_exc() 
        messages.error(request,"Unknown error. Please check later") 
        return HttpResponseRedirect("/")     

    log.debug("Found vars for the txn %s " % vars(detail))

    template = {'detail': detail}

    print template 
    return render_to_response(
        'aadhaar/txn.html', 
        template,
        RequestContext(request))

@login_required 
def history(request): 

    try:
        aadhaar = Aadhaar.objects.filter(user=request.user)[0]
    except: 
        aadhaar = None 
    try:
        authsummary = AadhaarAuthSummary.objects.filter(user=request.user)[0]
    except: 
        authsummary = None 
        
    try: 
        authdetails = AadhaarAuthDetails.objects.filter(user=request.user).order_by('-id')[:5]
    except: 
        authdetails = [] 

        
    template = {
        'aadhaar': aadhaar, 
        'authsummary': authsummary,
        'authdetails': authdetails
        }
    return render_to_response(
        'aadhaar/history.html', 
        template,
        RequestContext(request))
