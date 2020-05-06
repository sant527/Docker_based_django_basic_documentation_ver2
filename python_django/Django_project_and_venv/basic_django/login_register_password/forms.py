from custom_user.models import User
from django import forms
from basic_django import settings

class UserLoginViaOtpFormEmail(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    # we can create the email manually, but since its already defined we take advantage from model

    ############### important whenever for ease we use a field from a model################### 
    # if we dont call clean. it
    #will check for unique instance clause for email  and gives User already exists:
    #go to: class BaseModelForm(BaseForm): --- self._validate_unique = False
    def clean(self):
        return self.cleaned_data

from django.core.validators  import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django import forms

class UserLoginViaOtpFormOTP(forms.Form):

    otp_loginconfirm = forms.CharField(
                            help_text='Please Enter valid OTP sent to your Email', 
                            label='Otp', 
                            max_length=6,
                            validators=[RegexValidator(
                                        r'^\d{6}$',
                                        message=_('OTP shoud be of 6 digits'),
                                        code='invalid'
                                    )])