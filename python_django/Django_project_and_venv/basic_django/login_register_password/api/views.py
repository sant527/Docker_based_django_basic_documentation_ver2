import jwt
import json
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from basic_django import settings
from custom_user.models import User, UserSessionLog, ActionTypeForUserSessionLog
from login_register_password.forms import UserLoginViaOtpFormEmail, UserLoginViaOtpFormOTP
from django.contrib import messages
from basic_django.tasks import send_email_task
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import CsrfViewMiddleware
import secrets
import base64
import pyotp
from django_remote_forms.forms import RemoteForm
from django.core.serializers.json import DjangoJSONEncoder
import re
from django.template.loader import render_to_string
import datetime
import pytz
from django.utils.timezone import make_aware
from django.utils import timezone
from rest_framework import exceptions


###    ## LOGGING
import logging
import traceback
logger_custom_string = logging.getLogger("custom_string")
from basic_django import settings as settings_basic_django
#usage1: To show anything as string
#logger_custom_string.debug(settings_basic_django.anything("Hare Krishna",traceback.format_stack(limit=5)))
#usage2: to show dict or obj
#logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
#logger_custom_string.debug(settings_basic_django.pp_odir(obj,traceback.format_stack(limit=5)))  # This will pretty print all the properties from dir(obj)


# the following function will generate a pin using pyOTP and also a nonce
def generate_pin_pyopt():
    ### trying to generate a TOTP (time based One time password)
    # we create a nonce (number used once)
    # There three ways to create nonce
    #1) secrets.token_urlsafe() (we use this)
    #2) uuid.uuid4()
    #3) str(int(time.time()*1000))

    nonce = secrets.token_urlsafe()

    # we use pyotp to generate OTP based on current system time
    # pyotp needs a base32 secret  It uses an alphabet of A–Z,
    # followed by 2–7. 0 and 1 are skipped due to their similarity
    # with the letters O and I
    # we store the common secret in .env file
    base32_secret = settings_basic_django.SECRET_KEY_BASE32_PYOTP
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    django_secret = settings_basic_django.SECRET_KEY
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    # Now convert the nonce to base32
    # nonce.encode("UTF-8") - converts to bytes
    # base64.b32encode() gives byte string
    # .decode('utf-8') converts the byte string to string
    nonce_base32 = base64.b32encode(nonce.encode("utf-8")).decode('utf-8')
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    django_secret_base32 = base64.b32encode(django_secret.encode("utf-8")).decode('utf-8')
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    # the final secret we will use in pyotp is combination of
    # nonce_base32 + django_secret_base32 + base32_secret
    pyotp_secret = nonce_base32+django_secret_base32+base32_secret

    pyotp_secret_rep = re.sub(r'=', '', pyotp_secret)

    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    pin = pyotp.TOTP(pyotp_secret_rep,interval=settings_basic_django.TIMELIMIT_OTP).now()

    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
    return pin, nonce





# ???
@csrf_exempt
def user_login_via_otp_form_email(request):
# ???

    # messages_redirect are the those messages which we want to show after redirect
    # the client has to store them and pass on to the redirect url output
    # ??? Store all messages to be passed to the redirect url
    messages_redirect=[]
    # ???

    csrf_middleware = CsrfViewMiddleware()

    # response_data: is the python object which will be converted to json string and passed to httpresponse
    # ??? Store all the response data to be sent
    response_data = {}
    # ???

    import traceback
    logger_custom_string.debug(settings_basic_django.anything(request.method,traceback.format_stack(limit=5)))

    # ???
    if request.method == 'GET':
    # ???
        # Get form definition
        #form = UserLoginViaOtpFormEmail(initial={'email': settings.TESTING_EMAIL})
        # ??? get the form
        form = UserLoginViaOtpFormEmail()
        # ???
        logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

    # ???
    elif request.method == 'POST':
    # ???
        # if request.content_type  != 'application/json':
        #     return HttpResponse(json.dumps({"detail": "Unsupported media type \"'%s'\" in request." % request.content_type}), content_type="application/json",status=401);
        # # Process request for CSRF
        csrf_middleware.process_view(request, None, None, None)
        logger_custom_string.debug(settings_basic_django.anything(request.body,traceback.format_stack(limit=5)))

        # Check for request.body is proper json string.
        # ???
        try:
            # get form data from request.body
            form_data = json.loads(request.body)
            # ???
        except Exception as e:
            status_code = 400
            message = "The request body is not valid."
            # You should log this error because this usually means your front end has a bug.
            # do you whant to explain anything?
            explanation = "json.loads(request.body): "+str(e)
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return HttpResponse(
                  json.dumps({'message':message,'explanation':explanation}),
                  status=status_code,
                  content_type="application/json"
                )

        logger_custom_string.debug(settings_basic_django.pp_odir(form_data,traceback.format_stack(limit=5)))
        # ??? pass the form_data to form
        form = UserLoginViaOtpFormEmail(form_data)

        if form.is_valid():
        # ???

            # ??? Get the email
            email = form.cleaned_data.get('email')
            # ???

            # ??? Generate pin and nonce
            pin, nonce = generate_pin_pyopt()
            # ???
            # generate a random pin using crpto functions
            #pin = get_random_string(length=6, allowed_chars='1234567890')
            
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
            # ??? Email the pin
            send_email_task.delay(email,subject,message)
            # ???

            # ??? Create jwt_token with email, nonce and creation_time
            payload = {
                'email': email,
                'nonce': nonce,
                'creation_time': str(datetime.datetime.now(tz=pytz.timezone('UTC')).isoformat())
            }

            jwt_token = {
                        'token':jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                        }
            # ???

            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            # REDIRECTING TO A DIFFERENT VIEW ie. different URL
            logger_custom_string.debug(settings_basic_django.pp_odir(getattr(request, '_messages', []),traceback.format_stack(limit=5)))

            # ??? Create a message to show that OTP is sent to email
            messages_redirect.append('OTP send to email: ' + email)
            # ???

            # ??? Add all the data to be sent to the response_data object
            response_data.update({'messages_redirect': messages_redirect})
            response_data.update({'redirect': True})
            response_data.update({'redirect_url': reverse('login_register_password_namespace:login_register_password_api_app_name:user_login_via_otp_form_otp')})
            response_data.update(jwt_token)
            # ???

            # ??? Create json string
            response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
            # ???

            # ??? send the json_string of jwt_token
            return HttpResponse(
                  response_data_json_dumps,
                  status=200,
                  content_type="application/json"
                )
            # ???

    # ??? convert the form to dict
    remote_form = RemoteForm(form)
    remote_form_dict = remote_form.as_dict()
    # ???
    
    # ??? Add all the data to be sent to the response_data object
    response_data.update({'form': remote_form_dict})
    response_data.update({'messages_redirect': messages_redirect})
    response_data.update({'redirect': False})
    # ???

    # ??? create json string
    response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
    # ???



    # ??? Send the form as json string
    response = HttpResponse(
        response_data_json_dumps,
        content_type="application/json"
    )
    # ???

    # Process response for CSRF
    csrf_middleware.process_response(request, response)
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
    # ???
    return response
    # ???

# ???
@csrf_exempt
def user_login_via_otp_form_otp(request):
# ???

    # ??? Store all messages to be passed to the redirect url
    messages_redirect=[]
    # ???

    # ??? Store all the response data to be sent
    response_data = {}
    # ???

    # FORM
    # ???
    if request.method == 'POST':
    # ???

        import traceback
        #Eg: request.body
        # {
        #     "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InNpbWhhcnVwYS5ybnNAZ21haWwuY29tIiwibm9uY2UiOiJfVTluNXUwanYtNzJ6UjQzUTA1eEVTXzlmdEZBaWh1NlJiR1pFZ2E4VXUwIiwiY3JlYXRpb25fdGltZSI6IjIwMjAtMDMtMjBUMTI6NTc6MTcuNTUxNDc5KzAwOjAwIn0._lSMQwjAUtdvQfnwmQdNaM03mI3uYmZGZyGX_CXsK-M",
        #     "OTP":"943578"
        # }
        # ???
        try:
            # get form data from request.body
            form_data = json.loads(request.body)
            # ???
        except Exception as e:
            status_code = 400
            message = "The request body is not valid."
            # You should log this error because this usually means your front end has a bug.
            # do you whant to explain anything?
            explanation = "json.loads(request.body): "+str(e)
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return HttpResponse(
                  json.dumps({'message':message,'explanation':explanation}),
                  status=status_code,
                  content_type="application/json"
                )


        logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

        # ??? CHECKING whether data has jwt_token variable exists or not
        if 'jwt_token' in form_data:
            jwt_token = form_data['jwt_token']
        # ???
        else:
            status_code = 400
            message = "The request body is not valid."
            # You should log this error because this usually means your front end has a bug.
            # do you whant to explain anything?
            explanation = "jwt_token not found"
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return HttpResponse(
                  json.dumps({'message':message,'explanation':explanation}),
                  status=status_code,
                  content_type="application/json"
                )

        # ??? CHECKING jwt token and getting the payload
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
            # ???
            #logger_custom_string.debug(settings.pp_dict(payload))
        except Exception as e:  # NoQA
            status_code = 400
            message = "The request body is not valid."
            # You should log this error because this usually means your front end has a bug.
            # do you whant to explain anything?
            explanation = "jwt_token not valid"
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return HttpResponse(
                  json.dumps({'message':message,'explanation':explanation}),
                  status=status_code,
                  content_type="application/json"
                )

        # ??? checking if OTP exits in form Data
        if 'OTP' in form_data:
            OTP = form_data['OTP']
            # ???
        else:
            status_code = 400
            message = "The request body is not valid."
            # You should log this error because this usually means your front end has a bug.
            # do you whant to explain anything?
            explanation = "OTP param is not found"
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return HttpResponse(
                  json.dumps({'message':message,'explanation':explanation}),
                  status=status_code,
                  content_type="application/json"
                )

        # ??? Supplying the form data into the form
        form = UserLoginViaOtpFormOTP({"otp_loginconfirm":OTP})
        # ???
        logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

        # ??? checking if form is valid
        if form.is_valid():
            # ??? getting the cleaned data
            otp_loginconfirm = form.cleaned_data.get('otp_loginconfirm')
            # ???

            # ??? COMPARE TIME LIMIT FOR OTP (We check this using the time limit of jwt_token)
            #convert payload creation time to datetime
            creation_time = datetime.datetime.fromisoformat(payload['creation_time'])
            #datetime.timedelta(minutes=1, seconds=1)
            timelimit = datetime.timedelta(seconds=settings_basic_django.TIMELIMIT_OTP)
            current_time = datetime.datetime.now(tz=pytz.timezone('UTC'))
            timecheck = current_time - creation_time < timelimit
            timedelta = current_time - creation_time

            if current_time - creation_time > timelimit:
                form.add_error(None,"OTP expired, Click on resend OTP")
                remote_form = RemoteForm(form)
                remote_form_dict = remote_form.as_dict()
                # Errors in response_data['non_field_errors'] and response_data['errors']
                response_data.update({'form': remote_form_dict})
                response_data.update({'messages_redirect': messages_redirect})
                response_data.update({'redirect': False})
                response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
                response = HttpResponse(
                    response_data_json_dumps,
                    content_type="application/json"
                )
                return response
            # ???

            # ??? Generate TOTP based on the nonce
            ### trying to generate a TOTP (time based One time password)
            # we create a nonce (number used once)
            # There three ways to create nonce
            #1) secrets.token_urlsafe() (we use this)
            #2) uuid.uuid4()
            #3) str(int(time.time()*1000))

            nonce = payload['nonce']

            # we use pyotp to generate OTP based on current system time
            # pyotp needs a base32 secret  It uses an alphabet of A–Z,
            # followed by 2–7. 0 and 1 are skipped due to their similarity
            # with the letters O and I
            # we store the common secret in .env file
            base32_secret = settings_basic_django.SECRET_KEY_BASE32_PYOTP
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

            django_secret = settings_basic_django.SECRET_KEY
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

            # Now convert the nonce to base32
            # nonce.encode("UTF-8") - converts to bytes
            # base64.b32encode() gives byte string
            # .decode('utf-8') converts the byte string to string
            nonce_base32 = base64.b32encode(nonce.encode("utf-8")).decode('utf-8')

            django_secret_base32 = base64.b32encode(django_secret.encode("utf-8")).decode('utf-8')

            # the final secret we will use in pyotp is combination of
            # nonce_base32 + django_secret_base32 + base32_secret
            pyotp_secret = nonce_base32+django_secret_base32+base32_secret

            pyotp_secret_rep = re.sub(r'=', '', pyotp_secret)

            pin = pyotp.TOTP(pyotp_secret_rep,interval=settings_basic_django.TIMELIMIT_OTP).now()
            # ???

            # ??? Check the pin is valid
            if pin == form_data['OTP']: 
            # ???

                # ???
                try:
                # ???

                    # ??? check for existing user and save
                    match = User.objects.get(email=payload['email'])
                    time_now = timezone.now()
                    # if we do timezone.now(), (with a comma then it will save as tuple and will give error)
                    match.last_login2=time_now
                    match.recentdate_login_via_otp=time_now
                    match.save()
                    # ???
                    user_jwt_secret_main = match.jwt_secret

                    # ??? check match is active
                    if match.is_active:
                    # ???
                        #login(request,match,backend='django.contrib.auth.backends.ModelBackend')
                        logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
                    else:
                        messages_redirect.append(email + ' is not active')
                        response_data.update({'messages_redirect': messages_redirect})
                        response_data.update({'redirect': True})
                        response_data.update({'redirect_url': reverse('login_register_password_namespace:login_register_password_api_app_name:user_login_via_otp_form_email')})
                        response_data.update(jwt_token)
                        response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
                        return HttpResponse(
                              response_data_json_dumps,
                              status=200,
                              content_type="application/json"
                            )

                    #Get ip address
                    ip = settings.get_client_ip(request)

                    # get the action type
                    action_type = ActionTypeForUserSessionLog.objects.get(action='login_by_otp')

                    # Save in the session
                    match_UserSessionLog = UserSessionLog(
                        user_email=match.email,
                        ip_address = ip,
                        user = match,
                        otp_used_for_otplogin=form_data['OTP'],
                        action_type=action_type,
                        device_type=request.META['HTTP_USER_AGENT'],
                        # we use timezone.now without brackets in default, so if dont convert to string it throws error
                        # expected string or bytes-like object @ dateparse.py in parse_datetime, line 106
                        # here we 
                        created_time=time_now
                    )
                    match_UserSessionLog.save()
                    usersession_created_time = match_UserSessionLog.created_time
                    unique_id = match_UserSessionLog.unique_id
                    user_jwt_secret_session = match_UserSessionLog.jwt_secret
                    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
                    # ???

                # ???
                except User.DoesNotExist:
                # ???
                    """
                        total length of Model_meta.get_fields(include_hidden=True):  32
                        [
                            "<ManyToOneRel: admin.logentry>",
                            "<ManyToOneRel: custom_user.user_groups>",
                            "<ManyToOneRel: custom_user.user_user_permissions>",
                            "<ManyToOneRel: custom_user.usersessionlog>",
                            [
                                "<django.db.models.fields.AutoField: id>",
                                "STR: custom_user.User.id"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: last_login>",
                                "STR: custom_user.User.last_login"
                            ],
                            [
                                "<django.db.models.fields.BooleanField: is_superuser>",
                                "STR: custom_user.User.is_superuser"
                            ],
                            [
                                "<django.db.models.fields.BooleanField: is_staff>",
                                "STR: custom_user.User.is_staff"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: date_joined>",
                                "STR: custom_user.User.date_joined"
                            ],
                            [
                                "<django.db.models.fields.CharField: password>",
                                "STR: custom_user.User.password"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: recentdate_login_via_passwd>",
                                "STR: custom_user.User.recentdate_login_via_passwd"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: recentdate_login_via_otp>",
                                "STR: custom_user.User.recentdate_login_via_otp"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: recentdate_password_change>",
                                "STR: custom_user.User.recentdate_password_change"
                            ],
                            [
                                "<django.db.models.fields.CharField: first_name>",
                                "STR: custom_user.User.first_name"
                            ],
                            [
                                "<django.db.models.fields.CharField: last_name>",
                                "STR: custom_user.User.last_name"
                            ],
                            [
                                "<django.db.models.fields.EmailField: email>",
                                "STR: custom_user.User.email"
                            ],
                            [
                                "<django.db.models.fields.BooleanField: is_active>",
                                "STR: custom_user.User.is_active"
                            ],
                            [
                                "<django.db.models.fields.CharField: recent_otp_used_for_pass_change>",
                                "STR: custom_user.User.recent_otp_used_for_pass_change"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: date_of_recent_otp_used_for_pass_change>",
                                "STR: custom_user.User.date_of_recent_otp_used_for_pass_change"
                            ],
                            [
                                "<django.db.models.fields.CharField: otp_used_while_passlogin_create>",
                                "STR: custom_user.User.otp_used_while_passlogin_create"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: date_of_otp_used_while_passlogin_create>",
                                "STR: custom_user.User.date_of_otp_used_while_passlogin_create"
                            ],
                            [
                                "<django.db.models.fields.CharField: first_otp_used_for_otplogin>",
                                "STR: custom_user.User.first_otp_used_for_otplogin"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: date_of_first_otp_used_for_otplogin>",
                                "STR: custom_user.User.date_of_first_otp_used_for_otplogin"
                            ],
                            [
                                "<django.db.models.fields.TextField: about>",
                                "STR: custom_user.User.about"
                            ],
                            [
                                "<django.db.models.fields.CharField: location>",
                                "STR: custom_user.User.location"
                            ],
                            [
                                "<django.db.models.fields.DateField: birth_date>",
                                "STR: custom_user.User.birth_date"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: modified_date>",
                                "STR: custom_user.User.modified_date"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: creation_date>",
                                "STR: custom_user.User.creation_date"
                            ],
                            [
                                "<django.db.models.fields.DateTimeField: last_login2>",
                                "STR: custom_user.User.last_login2"
                            ],
                            [
                                "<django.db.models.fields.UUIDField: jwt_secret>",
                                "STR: custom_user.User.jwt_secret"
                            ],
                            [
                                "<django.db.models.fields.related.ManyToManyField: groups>",
                                "STR: custom_user.User.groups"
                            ],
                            [
                                "<django.db.models.fields.related.ManyToManyField: user_permissions>",
                                "STR: custom_user.User.user_permissions"
                            ]
                        ]


                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/async_helpers.py", line 68, in _pseudo_sync_runner
                            coro.send(None)
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3063, in run_cell_async
                            interactivity=interactivity, compiler=compiler, result=result)
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3254, in run_ast_nodes
                            if (await self.run_code(code, result, async_=asy)):
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3331, in run_code
                            exec(code_obj, self.user_global_ns, self.user_ns)
                          File "<ipython-input-5-0bf2236d2c30>", line 228, in <module>
                            print(settings.pp_odir(Model_meta.get_fields(include_hidden=True),traceback.format_stack(limit=5)))



                        Lenght of c_dict[000_null_true***********************************************************************]  9
                        Lenght of c_dict[001_remaining***********************************************************************]  1
                        Lenght of c_dict[002_null_false_and_empty_strings****************************************************]  10
                        Lenght of c_dict[003_auto_now_add__OR__auto_now******************************************************]  2
                        Lenght of c_dict[004_auto_created********************************************************************]  5
                        Lenght of c_dict[005_default_not_empty_string********************************************************]  5
                        Total lenght of c_dict:  32
                        {
                            "000_null_true***********************************************************************": {
                                "birth_date": {
                                    "000_class": "<class 'django.db.models.fields.DateField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                },
                                "date_of_first_otp_used_for_otplogin": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "date_of_otp_used_while_passlogin_create": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "date_of_recent_otp_used_for_pass_change": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "last_login": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                },
                                "last_login2": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                },
                                "recentdate_login_via_otp": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                },
                                "recentdate_login_via_passwd": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                },
                                "recentdate_password_change": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "005_null": true,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true
                                }
                            },
                            "001_remaining***********************************************************************": {
                            @@@@"jwt_secret": {
                                    "000_class": "<class 'django.db.models.fields.UUIDField'>",
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false,
                                    "editable": false,
                                    "max_length": 32
                                }
                            },
                            "002_null_false_and_empty_strings****************************************************": {
                                "about": {
                                    "000_class": "<class 'django.db.models.fields.TextField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "max_length": 500
                                },
                            @@@@"email": {
                                    "000_class": "<class 'django.db.models.fields.EmailField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": false,
                                    "max_length": 254,
                                    "unique": true
                                },
                                "first_name": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "max_length": 30
                                },
                            @@@@"first_otp_used_for_otplogin": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": false,
                                    "max_length": 6
                                },
                                "groups": {
                                    "000_class": "<class 'django.db.models.fields.related.ManyToManyField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "many_to_many": true,
                                    "one_to_many": false,
                                    "one_to_one": false,
                                    "remote_field": "<ManyToManyRel: custom_user.user>"
                                },
                                "last_name": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "max_length": 150
                                },
                                "location": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "max_length": 30
                                },
                                "otp_used_while_passlogin_create": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": false,
                                    "max_length": 6
                                },
                                "recent_otp_used_for_pass_change": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": false,
                                    "max_length": 6
                                },
                                "user_permissions": {
                                    "000_class": "<class 'django.db.models.fields.related.ManyToManyField'>",
                                    "001_default": "",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": true,
                                    "many_to_many": true,
                                    "one_to_many": false,
                                    "one_to_one": false,
                                    "remote_field": "<ManyToManyRel: custom_user.user>"
                                }
                            },
                            "003_auto_now_add__OR__auto_now******************************************************": {
                                "creation_date": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "003_auto_now_add": true,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true,
                                    "editable": false
                                },
                                "modified_date": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "004_auto_now": true,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true,
                                    "editable": false
                                }
                            },
                            "004_auto_created********************************************************************": {
                                "User_groups+": {
                                    "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                                    "002_auto_created": true,
                                    "005_null": true,
                                    "editable": false,
                                    "hidden": true,
                                    "many_to_many": false,
                                    "one_to_many": true,
                                    "one_to_one": false,
                                    "remote_field": [
                                        "<django.db.models.fields.related.ForeignKey: user>",
                                        "STR: custom_user.User_groups.user"
                                    ]
                                },
                                "User_user_permissions+": {
                                    "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                                    "002_auto_created": true,
                                    "005_null": true,
                                    "editable": false,
                                    "hidden": true,
                                    "many_to_many": false,
                                    "one_to_many": true,
                                    "one_to_one": false,
                                    "remote_field": [
                                        "<django.db.models.fields.related.ForeignKey: user>",
                                        "STR: custom_user.User_user_permissions.user"
                                    ]
                                },
                                "id": {
                                    "000_class": "<class 'django.db.models.fields.AutoField'>",
                                    "002_auto_created": true,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": true,
                                    "primary_key": true,
                                    "unique": true
                                },
                                "logentry": {
                                    "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                                    "002_auto_created": true,
                                    "005_null": true,
                                    "editable": false,
                                    "many_to_many": false,
                                    "one_to_many": true,
                                    "one_to_one": false,
                                    "remote_field": [
                                        "<django.db.models.fields.related.ForeignKey: user>",
                                        "STR: admin.LogEntry.user"
                                    ]
                                },
                                "usersessionlog": {
                                    "000_class": "<class 'django.db.models.fields.reverse_related.ManyToOneRel'>",
                                    "002_auto_created": true,
                                    "005_null": true,
                                    "editable": false,
                                    "many_to_many": false,
                                    "one_to_many": true,
                                    "one_to_one": false,
                                    "remote_field": [
                                        "<django.db.models.fields.related.ForeignKey: user>",
                                        "STR: custom_user.UserSessionLog.user"
                                    ]
                                }
                            },
                            "005_default_not_empty_string********************************************************": {
                                "date_joined": {
                                    "000_class": "<class 'django.db.models.fields.DateTimeField'>",
                                    "001_default": [
                                        "datetime.datetime(2020, 3, 14, 16, 27, 44, 363244, tzinfo=<UTC>)",
                                        "STR: 2020-03-14 16:27:44.363244+00:00"
                                    ],
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                            @@@@"is_active": {
                                    "000_class": "<class 'django.db.models.fields.BooleanField'>",
                                    "001_default": false,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "is_staff": {
                                    "000_class": "<class 'django.db.models.fields.BooleanField'>",
                                    "001_default": false,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "is_superuser": {
                                    "000_class": "<class 'django.db.models.fields.BooleanField'>",
                                    "001_default": false,
                                    "005_null": false,
                                    "006_empty_strings_allowed": false,
                                    "007_blank": false
                                },
                                "password": {
                                    "000_class": "<class 'django.db.models.fields.CharField'>",
                                    "001_default": "pbkdf2_sha256$180000$YoBw24luwZAV$0ZL6l6/5DgeRJv7FEGMswDP4kGM+tE04rSfA3FDqYbQ=",
                                    "005_null": false,
                                    "006_empty_strings_allowed": true,
                                    "007_blank": false,
                                    "max_length": 128
                                }
                            }
                        }


                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/async_helpers.py", line 68, in _pseudo_sync_runner
                            coro.send(None)
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3063, in run_cell_async
                            interactivity=interactivity, compiler=compiler, result=result)
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3254, in run_ast_nodes
                            if (await self.run_code(code, result, async_=asy)):
                          File "/home/web_dev/DO_NOT_DELETE_djang_basic_documentation_part2/.venv/lib/python3.7/site-packages/IPython/core/interactiveshell.py", line 3331, in run_code
                            exec(code_obj, self.user_global_ns, self.user_ns)
                          File "<ipython-input-5-0bf2236d2c30>", line 248, in <module>
                            print(settings.pp_odir(c_dict,traceback.format_stack(limit=5)))

                    """
                    # ??? Create a new user
                    time_now = timezone.now()
                    # if we do timezone.now(), (with a comma then it will save as tuple and will give error)
                    newuser = User(
                        email=payload['email'],
                        first_otp_used_for_otplogin=pin,
                        date_of_first_otp_used_for_otplogin=time_now,
                        last_login2=time_now,
                        recentdate_login_via_otp=time_now,
                        is_active=True
                        # we use timezone.now without brackets in default, so if dont convert to string it throws error
                        # expected string or bytes-like object @ dateparse.py in parse_datetime, line 106
                        #date_joined=time_now
                        )
                    newuser.save()
                    # ???

                    user_jwt_secret_main = newuser.jwt_secret

                    # Get the client ip:
                    ip = settings.get_client_ip(request)

                    action_type = ActionTypeForUserSessionLog.objects.get(action='login_by_otp')

                    # ??? Save in the session
                    new_UserSessionLog = UserSessionLog(
                        user_email=newuser.email,
                        ip_address = ip,
                        user = newuser,
                        otp_used_for_otplogin=pin,
                        action_type=action_type,
                        device_type=request.META['HTTP_USER_AGENT'],
                        created_time=time_now,
                    )

                    new_UserSessionLog.save()
                    # ???
                    unique_id = new_UserSessionLog.unique_id
                    user_jwt_secret_session = new_UserSessionLog.jwt_secret
                    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
                    usersession_created_time = new_UserSessionLog.created_time

                # ??? Create a message to show that OTP is sent to email
                messages_redirect.append('Login Successful')
                # ???

                # ??? Create token authenticating a user
                django_secret = settings_basic_django.SECRET_KEY

                # we also use the secret form Userssion and User tables
                user_toke_secret = django_secret + user_jwt_secret_main.hex + user_jwt_secret_session.hex
                payload_token = {
                    'email': payload['email'],
                    'creation_time': str(datetime.datetime.now(tz=pytz.timezone('UTC')).isoformat())
                }
                user_token = {
                    'token':jwt.encode(payload_token, user_toke_secret, algorithm='HS256').decode('utf-8'),
                    'unique_id':unique_id
                }
                # ???

                # ??? Add all the data to be sent to the response_data object
                response_data.update({'messages_redirect': messages_redirect})
                response_data.update({'redirect': True})
                response_data.update({'redirect_url': reverse('articles_namespace:articles')})
                response_data.update({"user_token":user_token})
                # ???

                # ??? Create json string
                response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
                # ???

                # ??? send the json_string of jwt_token
                return HttpResponse(
                  response_data_json_dumps,
                  status=200,
                  content_type="application/json"
                )
                # ???

            # ??? if form is not valid
            form.add_error(None,"Form Error: Wrong OTP entered")
            remote_form = RemoteForm(form)
            remote_form_dict = remote_form.as_dict()
            # Errors in response_data['non_field_errors'] and response_data['errors']
            response_data.update({'form': remote_form_dict})
            response_data.update({'messages_redirect': messages_redirect})
            response_data.update({'redirect': False})
            response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
            response = HttpResponse(
                response_data_json_dumps,
                content_type="application/json"
            )
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            return response
            # ???
    else:
        #logger_custom_string.debug(request.GET.get('resendotp'))
        #logger_custom_string.debug(settings.pp_dict(request.GET))
        #logger_custom_string.debug('resendotp' in request.GET)

        if 'resendotp' in request.GET:

            import traceback
            form_data = json.loads(request.body)
            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))

            # CHECKING whether the session variable exists or not
            if 'jwt_token' in form_data:
                jwt_token = form_data['jwt_token']
            else:
                status_code = 400
                message = "The request body is not valid."
                # You should log this error because this usually means your front end has a bug.
                # do you whant to explain anything?
                explanation = "jwt_token not found"
                logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
                return HttpResponse(
                      json.dumps({'message':message,'explanation':explanation}),
                      status=status_code,
                      content_type="application/json"
                    )

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
                status_code = 400
                message = "The request body is not valid."
                # You should log this error because this usually means your front end has a bug.
                # do you whant to explain anything?
                explanation = "jwt_token not valid"
                logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
                return HttpResponse(
                      json.dumps({'message':message,'explanation':explanation}),
                      status=status_code,
                      content_type="application/json"
                    )

            email = payload['email']

            pin, nonce = generate_pin_pyopt()
            # generate a random pin using crpto functions
            #pin = get_random_string(length=6, allowed_chars='1234567890')
            
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

            payload = {
                'email': email,
                'nonce': nonce,
                'creation_time': str(datetime.datetime.now(tz=pytz.timezone('UTC')).isoformat())
            }

            jwt_token = {
                        'token':jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                        }

            logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
            # REDIRECTING TO A DIFFERENT VIEW ie. different URL
            logger_custom_string.debug(settings_basic_django.pp_odir(getattr(request, '_messages', []),traceback.format_stack(limit=5)))

            messages_redirect.append('OTP send to email: ' + email)
            response_data.update({'messages_redirect': messages_redirect})
            response_data.update({'redirect': True})
            response_data.update({'redirect_url': reverse('login_register_password_namespace:login_register_password_api_app_name:user_login_via_otp_form_otp')})
            response_data.update(jwt_token)
            response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)
            return HttpResponse(
                  response_data_json_dumps,
                  status=200,
                  content_type="application/json"
                )

        form = UserLoginViaOtpFormOTP()

    remote_form = RemoteForm(form)
    remote_form_dict = remote_form.as_dict()
    # Errors in response_data['non_field_errors'] and response_data['errors']
    response_data.update({'form': remote_form_dict})
    response_data.update({'messages_redirect': messages_redirect})
    response_data.update({'redirect': False})


    response_data_json_dumps = json.dumps(response_data, cls=DjangoJSONEncoder)



    response = HttpResponse(
        response_data_json_dumps,
        content_type="application/json"
    )
    import traceback
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(), traceback.format_stack(limit=5)))
    return response


### #Basic one
### @csrf_exempt
### def user_login_via_otp_form_email(request):
###     response_data = {}
###     if request.method == 'GET':
###         # Get form definition
###         form = UserLoginViaOtpFormEmail(initial={'email': settings.TESTING_EMAIL})
###     elif request.method == 'POST':
###         form_data = json.loads(request.body)
###         logger_custom_string.debug(settings_basic_django.pp_odir(form_data,traceback.format_stack(limit=5)))
###         form = UserLoginViaOtpFormEmail(form_data)
###     html = "<html><body>API TESTING</body></html>"
###     return HttpResponse(html)


                


