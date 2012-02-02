#-*- coding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from uni_form.helpers import FormHelper, Submit, Reset
from django_auth_aadhaar.forms import AadhaarAuthForm 
from uni_form.layout import Layout,Fieldset, Div, Row, HTML
from captcha.fields import ReCaptchaField

class AadhaarLoginForm(AadhaarAuthForm):

    def __init__(self, *args, **kwargs):
        print "AadhaarLoginForm detail = "
        print "kwargs = ", kwargs
        print "args = ", args 
        super(AadhaarLoginForm, self).__init__(*args, **kwargs)
        
        # this would have set the level of detail. Now remove all 
        # unnecessary fields. 
        if self.detail == "personal":
            to_delete = [x[0] for x in AadhaarAuthForm.PA_ATTRIBUTES]
        elif self.detail == "address":
            to_delete = [x[0] for x in AadhaarAuthForm.PII_ATTRIBUTES]
        else:
            to_delete = []
        for field in to_delete:
            del self.fields[field]
            
        self.set_helper() 
        
    next     = forms.CharField(label="next", widget=forms.HiddenInput)
    # captcha = ReCaptchaField(label="Please enter text you see or hear")

    def set_helper(self):
        print "AadhaarLoginForm.helper In helper"
        #form = AadhaarLoginForm()
        helper = FormHelper()
        reset = Reset('','Reset')
        helper.add_input(reset)
        submit = Submit('','Authenticate')
        helper.add_input(submit)
        helper.form_action = '/aadhaar/authenticate/' + self.detail 
        helper.form_method = 'POST'
        helper.form_class="blueForms"

        style="""
<style>
fieldset.formRow {
         margin-bottom: 1em;
         border-width: 0 0 1px 0;
         border-color:#CCCCCC;
         border-style:solid;
}
</style>
"""
        common_layout =  Layout(
            Fieldset('Required Parameters',
                     'aadhaar_id',
                     'aadhaar_attributes',
                     )
            )
        pi_layout= Layout(
            Fieldset("Personally Identifiable Information",
                     'aadhaar_pi_match',
                     'aadhaar_name',
                     'aadhaar_dob', 
                     'aadhaar_age',
                     'aadhaar_gender',
                     'aadhaar_email',
                     'aadhaar_phone',
                     )
            )
        pa_layout = Layout(
            Fieldset("Address",
                     'aadhaar_pa_match',
                     'aadhaar_co',
                     'aadhaar_house',
                     'aadhaar_street',
                     'aadhaar_landmark',
                     'aadhaar_locality',
                     'aadhaar_vtc',
                     'aadhaar_subdist',
                     'aadhaar_district',
                     'aadhaar_state',
                     'aadhaar_pincode',
                     'aadhaar_postoffice')
            )
        
        if self.detail == "personal": 
            layout = Layout(common_layout, pi_layout)
        elif self.detail == "address":
            layout = Layout(common_layout, pa_layout)
        else:
            layout = Layout(common_layout, pi_layout, pa_layout)
            
        helper.layout = layout

        self.helper = helper
