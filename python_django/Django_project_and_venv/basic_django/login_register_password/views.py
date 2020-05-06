import jwt
import datetime
import pytz

from django.shortcuts import render, redirect
from django.http import HttpResponse
from basic_django import settings
from custom_user.models import User, UserSessionLog, ActionTypeForUserSessionLog
from django.utils.crypto import get_random_string
    
from django.template.loader import render_to_string
from .forms import UserLoginViaOtpFormEmail
from django.contrib import messages
from django.db.models.functions import Now
from django.utils.timezone import make_aware
from django.utils import timezone

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.urls import reverse

def set_debug():
    import pudb;pudb.set_trace()

# Create your views here.

###    ## LOGGING
import logging
import traceback
logger_custom_string = logging.getLogger("custom_string")
from basic_django import settings as settings_basic_django
#usage1: To show anything as string
#logger_custom_string.debug(settings_basic_django.anything("Hare Krishna",traceback.format_stack(limit=5)))
#usage2: to show dict or obj
#logger_custom_string.debug(settings_basic_django.pp_odir(locals(),traceback.format_stack(limit=5)))
#logger_custom_string.debug(settings_basic_django.pp_odir(obj,traceback.format_stack(limit=5)))  # This will pretty print all the properties from dir(obj)

from basic_django.tasks import send_email_task

def user_login_via_otp_form_email(request):

    ## CLEARING ALL THE MESSAGES
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    system_messages.used = True

    # TRYING to check if email is there in session.we want to delete it
    try:
        del request.session['email']
    except:
        pass

    try:
        del request.session['otp_modified_date_loginconfirm']
    except:
        pass

    #request.session.modified = True
    if request.method == 'POST':
        logger_custom_string.debug(settings_basic_django.pp_odir(request.POST,traceback.format_stack(limit=5)))
        form = UserLoginViaOtpFormEmail(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            # generate a random pin using crpto functions
            pin = get_random_string(length=6, allowed_chars='1234567890')
            
            # EMAIL subject and BODY
            # for BODY we use a template and render it with parameters
            subject = pin + ': To Login via OTP'
            # We to create the email body. So we create a template and pass the required arguments.
            # render_to_string will render the template with the context values
            message = render_to_string('login_register_password/login_via_otp/email/login_otp_sendemail.html', {
                'email': email,
                'pin': pin
            })

            # USING CELERY TASK for sending email Asynchronously
            #match.email_user(subject, message). This will delay the response 
            # So will do this task asynchronously using celery
            # We have created a celery task. Using it we will send the email.
            # The code does not have to wait till the email is sent
            send_email_task.delay(email,subject,message)

            #USING MESSAGES to inform the user in the next page about email is being sent
            #we want to inform the user on the next page that email is being sent for OTP
            #For this we use messages
            messages.success(request, 'Email is being sent please check')

            payload = {
                'email': email,
                'OTP': pin,
                'creation_time': str(datetime.datetime.now(tz=pytz.timezone('UTC')).isoformat())
            }

            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
            # USING SESSION to make data available to next view.
            #For the next page we want to send some data which we dont want to display.
            request.session['jwt_token'] = jwt_token
            #logger_custom_string.debug(jwt_token)

            # REDIRECTING TO A DIFFERENT VIEW ie. different URL
            return redirect('login_register_password_namespace:user_login_via_otp_form_otp')
    else:
        form = UserLoginViaOtpFormEmail(initial={'email': settings.TESTING_EMAIL})
        
    return render(request, 'login_register_password/login_via_otp/user_login_via_otp_form_email.html', {'form': form})




def user_login_via_otp_form_otp(request):
    ## CLEARING ALL THE MESSAGES
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    system_messages.used = True


    # CHECKING whether the session variable exists or not
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
    else:
        messages.error(request, 'jwt_token in session not found')
        return redirect('login_register_password_namespace:user_login_via_otp_form_email')

    # CHECKING jwt token and getting the payload
    try:
        # options = {
        #     'verify_exp': True,
        # }
        payload = jwt.decode(
            jwt_token,
            settings.SECRET_KEY,
            True,
            #options=options,
        )
        #logger_custom_string.debug(settings.pp_dict(payload))
    except Exception as e:  # NoQA
        #logger_custom_string.debug(str(e))
        pass

    # FORM
    from .forms import UserLoginViaOtpFormOTP
    if request.method == 'POST':

        form = UserLoginViaOtpFormOTP(request.POST)
        if form.is_valid():
            otp_loginconfirm = form.cleaned_data.get('otp_loginconfirm')

            #COMPARE TIME LIMIT FOR OTP

            #convert payload creation time to datetime
            creation_time = datetime.datetime.fromisoformat(payload['creation_time'])
            #datetime.timedelta(minutes=1, seconds=1)
            timelimit = datetime.timedelta(seconds=10)
            current_time = datetime.datetime.now(tz=pytz.timezone('UTC'))
            timecheck = current_time - creation_time < timelimit
            timedelta = current_time - creation_time
            import traceback
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(),traceback.format_stack(limit=5)))

            if current_time - creation_time > timelimit:
                form.add_error(None,"OTP expired, Click on resend OTP")
                return render(request, 'login_register_password/login_via_otp/user_login_via_otp_form_otp.html',{'form': form})

            if payload['OTP'] == otp_loginconfirm:

                # CHECK for an existing user
                try:

                    match = User.objects.get(email=payload['email'])
                    time_now = timezone.now()
                    # if we do timezone.now(), (with a comma then it will save as tuple and will give error)
                    match.last_login2=time_now
                    match.recentdate_login_via_otp=time_now
                    match.save()

                    if match.is_active:
                        login(request,match,backend='django.contrib.auth.backends.ModelBackend')
                    else:
                        messages(email, ' :not active')
                        return redirect('login_register_password_namespace:user_login_via_otp_form_email')

                    #Get ip address
                    ip = settings.get_client_ip(request)

                    # get the action type
                    action_type = ActionTypeForUserSessionLog.objects.get(action='login_by_otp')

                    # Save in the session
                    match_UserSessionLog = UserSessionLog(
                        user_email=match.email,
                        ip_address = ip,
                        user = match,
                        otp_used_for_otplogin=payload['OTP'],
                        action_type=action_type,
                        device_type=request.META['HTTP_USER_AGENT'],
                        created_time=time_now
                    )

                    match_UserSessionLog.save()
                    
                except User.DoesNotExist:
                    #we create a new user

                        ###   total length of Model_meta.get_fields(include_hidden=True):  31
                        ###   
                        ###   
                        ###   [
                        ###       "<ManyToOneRel: admin.logentry>",
                        ###       "<ManyToOneRel: custom_user.user_groups>",
                        ###       "<ManyToOneRel: custom_user.user_user_permissions>",
                        ###       "<ManyToOneRel: custom_user.usersessionlog>",
                        ###       [
                        ###           "<django.db.models.fields.AutoField: id>",
                        ###           "STR: custom_user.User.id"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: last_login>",
                        ###           "STR: custom_user.User.last_login"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.BooleanField: is_superuser>",
                        ###           "STR: custom_user.User.is_superuser"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.BooleanField: is_staff>",
                        ###           "STR: custom_user.User.is_staff"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: date_joined>",
                        ###           "STR: custom_user.User.date_joined"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: password>",
                        ###           "STR: custom_user.User.password"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: recentdate_login_via_passwd>",
                        ###           "STR: custom_user.User.recentdate_login_via_passwd"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: recentdate_login_via_otp>",
                        ###           "STR: custom_user.User.recentdate_login_via_otp"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: recentdate_password_change>",
                        ###           "STR: custom_user.User.recentdate_password_change"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: first_name>",
                        ###           "STR: custom_user.User.first_name"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: last_name>",
                        ###           "STR: custom_user.User.last_name"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.EmailField: email>",
                        ###           "STR: custom_user.User.email"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.BooleanField: is_active>",
                        ###           "STR: custom_user.User.is_active"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: recent_otp_used_for_pass_change>",
                        ###           "STR: custom_user.User.recent_otp_used_for_pass_change"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: date_of_recent_otp_used_for_pass_change>",
                        ###           "STR: custom_user.User.date_of_recent_otp_used_for_pass_change"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: otp_used_while_passlogin_create>",
                        ###           "STR: custom_user.User.otp_used_while_passlogin_create"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: date_of_otp_used_while_passlogin_create>",
                        ###           "STR: custom_user.User.date_of_otp_used_while_passlogin_create"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: first_otp_used_for_otplogin>",
                        ###           "STR: custom_user.User.first_otp_used_for_otplogin"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: date_of_first_otp_used_for_otplogin>",
                        ###           "STR: custom_user.User.date_of_first_otp_used_for_otplogin"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.TextField: about>",
                        ###           "STR: custom_user.User.about"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.CharField: location>",
                        ###           "STR: custom_user.User.location"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateField: birth_date>",
                        ###           "STR: custom_user.User.birth_date"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: modified_date>",
                        ###           "STR: custom_user.User.modified_date"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: creation_date>",
                        ###           "STR: custom_user.User.creation_date"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.DateTimeField: last_login2>",
                        ###           "STR: custom_user.User.last_login2"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.related.ManyToManyField: groups>",
                        ###           "STR: custom_user.User.groups"
                        ###       ],
                        ###       [
                        ###           "<django.db.models.fields.related.ManyToManyField: user_permissions>",
                        ###           "STR: custom_user.User.user_permissions"
                        ###       ]
                        ###   ]
                        ###   
                        ###   
                        ###   
                        ###   Lenght of c_dict[000_null_true***********************************************************************]  8
                        ###   Lenght of c_dict[001_remaining***********************************************************************]  1
                        ###   Lenght of c_dict[002_null_false_and_empty_strings****************************************************]  10
                        ###   Lenght of c_dict[003_auto_now_add__OR__auto_now******************************************************]  2
                        ###   Lenght of c_dict[004_auto_created********************************************************************]  5
                        ###   Lenght of c_dict[005_default_not_empty_string********************************************************]  5
                        ###   Total lenght of c_dict:  31
                        ###   {
                        ###       "000_null_true***********************************************************************": {
                        ###           "birth_date": {
                        ###               "000_class": "<class 'django.db.models.fields.DateField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           },
                        ###@@@@       "date_of_first_otp_used_for_otplogin": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "date_of_otp_used_while_passlogin_create": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "date_of_recent_otp_used_for_pass_change": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "last_login": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           },
                        ###@@@@       "recentdate_login_via_otp": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           },
                        ###           "recentdate_login_via_passwd": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           },
                        ###           "recentdate_password_change": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": true,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           }
                        ###       },
                        ###       "001_remaining***********************************************************************": {
                        ###@@@@       "last_login2": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true
                        ###           }
                        ###       },
                        ###       "002_null_false_and_empty_strings****************************************************": {
                        ###           "about": {
                        ###               "000_class": "<class 'django.db.models.fields.TextField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "max_length": 500
                        ###           },
                        ###@@@@       "email": {
                        ###               "000_class": "<class 'django.db.models.fields.EmailField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": false,
                        ###               "max_length": 254,
                        ###               "unique": true
                        ###           },
                        ###           "first_name": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "max_length": 30
                        ###           },
                        ###@@@@       "first_otp_used_for_otplogin": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": false,
                        ###               "max_length": 6
                        ###           },
                        ###           "groups": {
                        ###               "000_class": "<class 'django.db.models.fields.related.ManyToManyField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "many_to_many": true,
                        ###               "one_to_many": false,
                        ###               "one_to_one": false,
                        ###               "remote_field": "<ManyToManyRel: custom_user.user>"
                        ###           },
                        ###           "last_name": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "max_length": 150
                        ###           },
                        ###           "location": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "max_length": 30
                        ###           },
                        ###           "otp_used_while_passlogin_create": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": false,
                        ###               "max_length": 6
                        ###           },
                        ###           "recent_otp_used_for_pass_change": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": false,
                        ###               "max_length": 6
                        ###           },
                        ###           "user_permissions": {
                        ###               "000_class": "<class 'django.db.models.fields.related.ManyToManyField'>",
                        ###               "001_default": "",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": true,
                        ###               "many_to_many": true,
                        ###               "one_to_many": false,
                        ###               "one_to_one": false,
                        ###               "remote_field": "<ManyToManyRel: custom_user.user>"
                        ###           }
                        ###       },
                        ###       "003_auto_now_add__OR__auto_now******************************************************": {
                        ###           "creation_date": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "003_auto_now_add": true,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true,
                        ###               "editable": false
                        ###           },
                        ###           "modified_date": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "004_auto_now": true,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true,
                        ###               "editable": false
                        ###           }
                        ###       },
                        ###       "004_auto_created********************************************************************": {
                        ###           "User_groups+": {
                        ###               "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                        ###               "002_auto_created": true,
                        ###               "005_null": true,
                        ###               "editable": false,
                        ###               "hidden": true,
                        ###               "many_to_many": false,
                        ###               "one_to_many": true,
                        ###               "one_to_one": false,
                        ###               "remote_field": [
                        ###                   "<django.db.models.fields.related.ForeignKey: user>",
                        ###                   "STR: custom_user.User_groups.user"
                        ###               ]
                        ###           },
                        ###           "User_user_permissions+": {
                        ###               "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                        ###               "002_auto_created": true,
                        ###               "005_null": true,
                        ###               "editable": false,
                        ###               "hidden": true,
                        ###               "many_to_many": false,
                        ###               "one_to_many": true,
                        ###               "one_to_one": false,
                        ###               "remote_field": [
                        ###                   "<django.db.models.fields.related.ForeignKey: user>",
                        ###                   "STR: custom_user.User_user_permissions.user"
                        ###               ]
                        ###           },
                        ###           "id": {
                        ###               "000_class": "<class 'django.db.models.fields.AutoField'>",
                        ###               "002_auto_created": true,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": true,
                        ###               "primary_key": true,
                        ###               "unique": true
                        ###           },
                        ###           "logentry": {
                        ###               "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                        ###               "002_auto_created": true,
                        ###               "005_null": true,
                        ###               "editable": false,
                        ###               "many_to_many": false,
                        ###               "one_to_many": true,
                        ###               "one_to_one": false,
                        ###               "remote_field": [
                        ###                   "<django.db.models.fields.related.ForeignKey: user>",
                        ###                   "STR: admin.LogEntry.user"
                        ###               ]
                        ###           },
                        ###           "usersessionlog": {
                        ###               "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                        ###               "002_auto_created": true,
                        ###               "005_null": true,
                        ###               "editable": false,
                        ###               "many_to_many": false,
                        ###               "one_to_many": true,
                        ###               "one_to_one": false,
                        ###               "remote_field": [
                        ###                   "<django.db.models.fields.related.ForeignKey: user>",
                        ###                   "STR: custom_user.UserSessionLog.user"
                        ###               ]
                        ###           }
                        ###       },
                        ###       "005_default_not_empty_string********************************************************": {
                        ###@@@@       "date_joined": {
                        ###               "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                        ###               "001_default": [
                        ###                   "datetime.datetime(2019, 10, 12, 1, 16, 2, 339774, tzinfo=<UTC>)",
                        ###                   "STR: 2019-10-12 01:16:02.339774+00:00"
                        ###               ],
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###@@@@       "is_active": {
                        ###               "000_class": "<class 'django.db.models.fields.BooleanField'>",
                        ###               "001_default": false,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "is_staff": {
                        ###               "000_class": "<class 'django.db.models.fields.BooleanField'>",
                        ###               "001_default": false,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "is_superuser": {
                        ###               "000_class": "<class 'django.db.models.fields.BooleanField'>",
                        ###               "001_default": false,
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": false,
                        ###               "007_blank": false
                        ###           },
                        ###           "password": {
                        ###               "000_class": "<class 'django.db.models.fields.CharField'>",
                        ###               "001_default": "pbkdf2_sha256$150000$zV7im78Gkp9T$zv2vl1sYuqtAaoWhjn7jpdHIoY2mzFKrtsN9MiR37SQ=",
                        ###               "005_null": false,
                        ###               "006_empty_strings_allowed": true,
                        ###               "007_blank": false,
                        ###               "max_length": 128
                        ###           }
                        ###       }
                        ###   }

                    time_now = timezone.now()
                    # if we do timezone.now(), (with a comma then it will save as tuple and will give error)
                    newuser = User(
                        email=payload['email'],
                        first_otp_used_for_otplogin=payload['OTP'],
                        date_of_first_otp_used_for_otplogin=time_now,
                        last_login2=time_now,
                        recentdate_login_via_otp=time_now,
                        is_active=True,
                        # we use timezone.now without brackets in default, so if dont convert to string it throws error
                        # expected string or bytes-like object @ dateparse.py in parse_datetime, line 106
                        date_joined=time_now
                        )
                    newuser.save()

                    if newuser.is_active:
                        login(request,newuser,backend='django.contrib.auth.backends.ModelBackend')
                    else:
                        messages(email, ' :not active')
                        return redirect('login_register_password_namespace:user_login_via_otp_form_email')


                    # Get the client ip:
                    ip = settings.get_client_ip(request)

                    action_type = ActionTypeForUserSessionLog.objects.get(action='login_by_otp')



                    # Save in the session
                    new_UserSessionLog = UserSessionLog(
                        user_email=newuser.email,
                        ip_address = ip,
                        user = newuser,
                        otp_used_for_otplogin=payload['OTP'],
                        action_type=action_type,
                        device_type=request.META['HTTP_USER_AGENT'],
                        created_time=time_now
                    )

                    new_UserSessionLog.save()

                messages.success(request, 'Login successful')
                return redirect('articles_namespace:articles')

            form.add_error(None,"Form Error: Wrong OTP entered")
            return render(request, 'login_register_password/login_via_otp/user_login_via_otp_form_otp.html',{'form': form})
    else:
        #logger_custom_string.debug(request.GET.get('resendotp'))
        #logger_custom_string.debug(settings.pp_dict(request.GET))
        #logger_custom_string.debug('resendotp' in request.GET)

        if 'resendotp' in request.GET:

            email = payload['email']
            # generate a random pin using crpto functions
            pin = get_random_string(length=6, allowed_chars='1234567890')
            
            # EMAIL subject and BODY
            # for BODY we use a template and render it with parameters
            subject = pin + ': To Login via OTP'
            # We to create the email body. So we create a template and pass the required arguments.
            # render_to_string will render the template with the context values
            message = render_to_string('login_register_password/login_via_otp/email/login_otp_sendemail.html', {
                'email': email,
                'pin': pin
            })

            # USING CELERY TASK for sending email Asynchronously
            #match.email_user(subject, message). This will delay the response 
            # So will do this task asynchronously using celery
            # We have created a celery task. Using it we will send the email.
            # The code does not have to wait till the email is sent
            send_email_task.delay(email,subject,message)

            #USING MESSAGES to inform the user in the next page about email is being sent
            #we want to inform the user on the next page that email is being sent for OTP
            #For this we use messages
            messages.success(request, 'Email is being sent please check')

            payload = {
                'email': email,
                'OTP': pin,
                'creation_time': str(datetime.datetime.now(tz=pytz.timezone('UTC')).isoformat())
            }

            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
            # USING SESSION to make data available to next view.
            #For the next page we want to send some data which we dont want to display.
            request.session['jwt_token'] = jwt_token
            #logger_custom_string.debug(jwt_token)

        else:
            # Want to check no one access this page directy. But only through the user_login_via_otp_form_email pages
            try:
                prev_url = request.META['HTTP_REFERER']

                # we want to get the url from namespace . We use reverse. But this give relative url not the full url with domain
                login_form_email_url_reverse = reverse("login_register_password_namespace:user_login_via_otp_form_email")
                # to get the full url we have to use do the below
                login_form_email_url_reverse_full = request.build_absolute_uri(login_form_email_url_reverse)

                #logger_custom_string.debug(prev_url)
                #logger_custom_string.debug(login_form_email_url_reverse_full)
                if prev_url != login_form_email_url_reverse_full:
                    #logger_custom_string.debug(prev_url != login_form_email_url_reverse_full)
                    return redirect('login_register_password_namespace:user_login_via_otp_form_email')
            except Exception as e:
                messages.error(request, str(e))
                #logger_custom_string.debug(str(e))
                return redirect('login_register_password_namespace:user_login_via_otp_form_email')

        form = UserLoginViaOtpFormOTP(initial={'otp_loginconfirm': payload['OTP']})
    return render(request, 'login_register_password/login_via_otp/user_login_via_otp_form_otp.html',{'form': form})


def logout_view(request):
    # never use the same name as logout(request) it will cause recurssion error
    email = request.user.email
    logout(request)

    ## CLEARING ALL THE MESSAGES
    system_messages = messages.get_messages(request)
    for message in system_messages:
        # This iteration is necessary
        pass
    system_messages.used = True
    messages.success(request, email + ' has logged out successfully')
    return redirect('articles_namespace:articles')


from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import CsrfViewMiddleware
from django_remote_forms.forms import RemoteForm
import json
from .forms import UserLoginViaOtpFormEmail
from django.http import HttpResponse


@csrf_exempt
def api_user_login_via_otp_form_email_django_forms_example(request):
    csrf_middleware = CsrfViewMiddleware()

    response_data = {}
    if request.method == 'GET':
        # Get form definition
        form = UserLoginViaOtpFormEmail(initial={'email': settings.TESTING_EMAIL2})
    elif request.method == 'POST':
        if request.content_type  != 'application/json':
            return HttpResponse(json.dumps({"detail": "Unsupported media type \"'%s'\" in request." % request.content_type}), content_type="application/json",status=401);
        # Process request for CSRF
        csrf_middleware.process_view(request, None, None, None)
        form_data = json.loads(request.body)
        form = UserLoginViaOtpFormEmail(form_data)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            response = HttpResponse(
                {'email': email},
                content_type="application/json"
            )

    remote_form = RemoteForm(form)
    # Errors in response_data['non_field_errors'] and response_data['errors']
    response_data.update(remote_form.as_dict())

    response = HttpResponse(
        json.dumps(response_data, cls=DjangoJSONEncoder),
        content_type="application/json"
    )

    # Process response for CSRF
    csrf_middleware.process_response(request, response)
    return response
