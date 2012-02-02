#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
import time 

def homepage(request):
    
    print vars(request.session)
    print vars(request.user) 

    template = {}
    return render_to_response(
        'base/homepage.html', 
        template, 
        RequestContext(request))
