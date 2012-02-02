from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    (r'^account/', include('aadhaartest.apps.account.urls')),
    (r'^aadhaar/', include('django_aadhaar.urls')),
    (r'^/?$', include('aadhaartest.apps.base.urls')),
)


