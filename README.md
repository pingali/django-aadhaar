Aadhaar Authentication Service Module
-------------------------------------

This module builds on python infrastructure for Aadhaar
([pyAadhaarAuth](http://github.com/pingali/pyAadhaarAuth)
authentication library and the
[django-auth-aadhaar](http://github.com/pingali/django-auth-aadhaar)
authentication backend) to provide a simple drop in module for adding
Aadhaar authentication to any Django website. It should take 5-10
minutes to add aadhaar to your favorite project! Users, once
authenticated, can be authenticated and marked aadhaar verified. You
can use that aadhaar verified status to provide additional services.

Usage
-----

The module is installed as an app into the django application. The
module provides urls and one command. The command installs the
configuration files required for aadhaar authentication. Once the
settings.py and urls.py are updated, and the configuration files
installed, we are good to go. 

The URLs provided include: 

1. /aadhaar/authenticate/personal - Authentication of PII. You can
   authenticate address (/aadhaar/authenticate/address) and both
   together (/aadhaar/authenticate/all) 

2. /aadhaar/txn/&lt;txn-id&gt;/ - Show the results of a given authentication
   request.
   
3. /aadhaar/history - Shows the history of successful and unsuccessful
   authentications performed by the user. 

Installation 
------------

The following instructions are for Ubuntu 11.10 but should work on 
other versions of Ubuntu. 

*  Install libraries and their dependencies 

    Follow instructions on the repository pages 
	[pyAadhaarAuth](http://github.com/pingali/pyAadhaarAuth) and
	[django-auth-aadhaar](http://github.com/pingali/django-auth-aadhaar)
		
	The libraries are not yet part of the standard package
	repositories. Pay particular attention to the M2Crypto package 
	installation instruction. 

* Install dependencies (for django_aadhaar) 

>       $ sudo easy_install django-uni-form 
>       $ sudo easy_install python-dateutil==1.5 

The next few steps depend on the application you are trying to add
django_aadhaar to. The module comes with an example application - [django-aadhaar/example/aadhaartest](https://github.com/pingali/django-aadhaar/tree/master/example/aadhaartest) that already has django_aadhaar installed.  

* Install dependencies (for aadhaartest) 

>       $ sudo easy_install django south netifaces django-recaptcha 

* Add django_aadhaar to the apps list (settings.py)

>        INSTALLED_APPS = (
>        ...
>           'django_aadhaar',
>        ) 

* Add authentication paths to valid URLs (urls.py) 

>        ...
>        (r'^aadhaar/', include('django_aadhaar.urls')),
>        ...

* Install Aadhaar authentication configuration information

    This *aadhaarinit* command will add a *fixtures* directory and
    within that all the files required for Aadhaar
    authentication. Please see
    [pyAadhaarAuth](http://github.com/pingali/pyAadhaarAuth) for
    documentation on the configuration and remaining files. When
    Aadhaar Authentication goes live, you have to update these files.
	
>       
>       $ python manage.py aadhaarinit 


* Sync the database 

>       $ python manage.my syncdb 
>       $ python manage.my migrate (if using south) 

* Restart the server and visit [http://localhost:8000/aadhaar/history](http://localhost:8000/aadhaar/history) 

Known Issues 
------------

1. dateutil  iter() returned non-iterator of type _timelex

	Make sure you install python-dateutil==1.5 
