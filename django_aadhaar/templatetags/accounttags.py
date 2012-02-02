from django import template
import textwrap 
from django_auth_aadhaar.forms import AadhaarAuthForm
 
register = template.Library()

def truncatelen(s, arg):
    if ((arg > len(s) - 3) or (arg < 4)): 
        return s 
    truncated_s =  "%s..." % s[1:arg-3]
    return truncated_s

def wrap(s, arg):
    return textwrap.wrap(s, arg)

def get_enabled_flags(bits): 
    # attrlist = ((name, description),...)
    attr_list = AadhaarAuthForm.PII_ATTRIBUTES + AadhaarAuthForm.PA_ATTRIBUTES
    y = []
    for f in bits:
        # f = (name, True/False) 
        if f[1]: 
            attr_name = f[0] 
            for (i,v) in enumerate(attr_list):
                if (v[0] == attr_name):
                    y.append(v[1])
                    break

    if len(y) == 0: 
        return "No flags enabled"
    else: 
        return ",".join(y) 

register.filter('truncatelen',truncatelen)
register.filter('wrap',wrap)
register.filter('get_enabled_flags',get_enabled_flags)

