#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django_aadhaar.views',
    (r'^authenticate/(?P<detail>\w+)?$',    'authenticate'),
    (r'^txn/(?P<txn_id>\S+)/$',    'txn'),
    (r'^history/$',    'history'),
)
