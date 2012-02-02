#-*- coding: utf-8 -*-

from django.conf import settings 
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages 
from .forms import SignupForm, LoginForm, CreateClientForm, ClientRemoveForm, ProfileForm 
import simplejson as json
#from django_aadhaar.models import AadhaarAuthSummary, Aadhaar, AadhaarAuthDetails 
from django_auth_aadhaar.forms import AadhaarAuthForm 
import logging 

log = logging.getLogger("aadhaartest.apps.account.views") 

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"])
            if user is not None: 
                if user.is_active: 
                    auth.login(request, user)
                    messages.success(request, "Welcome %s" % user.username)
                    if request.POST.get('next'):
                        next = form.cleaned_data['next'] 
                    else:
                        next = "/"
                else: 
                    messages.error(request, "User %s is not active" % user.username)
                    next = "/"
            else: 
                messages.error(request, "User does not exist")
                next = "/account/login" 
            print "[POST] redirecting from login page to ", next 
            return HttpResponseRedirect(next) 

    else:
        # Support redirect
        initial = {} 
        if request.GET.get('next') != None: 
            next = request.GET.get('next')
            initial['next'] = next 
            print "[GET] redirecting from login page to ", next 
        form = LoginForm(initial=initial)
        
    template = {"form":form}
    return render_to_response(
        'account/login.html', 
        template, 
        RequestContext(request))
 
    
@login_required    
def logout(request):
    auth.logout(request)
    return render_to_response(
        'account/logout.html', 
        {}, 
        RequestContext(request))


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                    form.cleaned_data["username"],
                    form.cleaned_data["email"],
                    form.cleaned_data["password1"],)
            user = auth.authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"])
            auth.login(request, user)
            messages.success(request, "Welcome %s!" % user.username)
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    template = {"form":form}
    return render_to_response(
        'account/signup.html', 
        template, 
        RequestContext(request))

