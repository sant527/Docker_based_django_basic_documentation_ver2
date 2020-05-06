from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, ValidationError,
    )

from django.contrib.auth import password_validation
import uuid
from django.core.validators  import RegexValidator,MinLengthValidator


###############################
## LOGGING
import logging
logger_custom_string = logging.getLogger("custom_string")
from basic_django import settings
#usage:
#logger_custom_string.debug(settings.pp_odir(user_set))  # This will pretty print all the properties from dir(user_set)
#sql = str(user_set.query)
#sql = user_set.query.__str__()
#logger_custom_string.debug(settings.pp_sql_sql(sql)) # pretty print the sql obtained from the .query
#logger_custom_string.debug(settings.pp_sql_query_pg(user_set)) # pretty print the sql using mogrify only possible with Psycopg
#logger_custom_string.debug(settings.pp_sql_query_any(user_set)) # pretty print the sql using EXPLAIN. But runs extra sql
#import traceback
#logger_custom_string.debug(settings.pp_traceback(traceback.format_stack())) #test traceback
logger_database = logging.getLogger("django.db.backends")
#usage:
#logger_database.filters[0].open()
#logger_database.filters[0].close()


import string
import secrets
def generateSecureRandomString(stringLength=20):
    """Generate a secure random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(password_characters) for i in range(stringLength))



# We want to use email as the login. The default User Manager () at 
# /venv_btg/lib/python3.6/site-packages/django/contrib/auth/models.py 
# is made for username based so we have to  rewrite to email based


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    # You can optionally serialize managers into migrations and have them available in
    # RunPython operations. This is done by defining a use_in_migrations attribute on
    # the manager class:

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')

        # what is normalizing_email
        # For email addresses, foo@bar.com and foo@BAR.com are equivalent;
        # the domain part is case-insensitive according to the RFC specs.
        # Normalizing means providing a canonical representation,
        # so that any two equivalent email strings normalize to the same thing.
        # The comments on the Django method explain:
        # Normalize the email address by lowercasing the domain part of it.

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)


        # What is self.model() in django custom UserManager
        
        # Well what you define here is a UserManager class. This inherits from
        # the BaseUserManager class. This is a subclass of the Manager class.
        # You actually use manager all the time. For example SomeModel.objects
        # is a manager.

        # A manager has, if it is used, a reference to the model it manages.
        # So SomeModel.objects is a manager, but that manager has an attribute
        # .model that actually refers back to the SomeModel class.

        # In this case your self.model will refer to User model


        # Sets the user’s password to the given raw string, taking care of the password hashing.
        # Doesn’t save the User object.
        user.set_password(password)
        
        user.save(using=self._db)
        
        return user

        # Q: using model.save() from django shell will not validate the data

        # Creating an instance of a Model and calling save on that instance
        # does not call full_clean. Therefore it’s possible for invalid data
        # to enter your database if you don’t manually call the full_clean
        # function before saving.

        # Object managers’ default create function also doesn’t call full_clean.

        # But in general, it's not good practice to add validation in the
        # save() method. The reason is that in most Django apps, you'd create
        # a form (a ModelForm) which would call the validation methods and be
        # able to return something meaningful to the user when validation
        # fails.

        # When the model's save() method is called it's too late to show
        # something to the user, so you can only raise an exception at that
        # point (and crash).

        # The normal procedure (which the admin forms use) is: validate the
        # form by calling form.is_valid() (which calls full_clean() on the
        # model), then if and only if the form is valid, save the model.

        # The shell is not the regular interaction method and should be used
        # only very carefully as it bypasses the normal flow of the
        # application.



    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        # What setdefault function does is that while creating a user if the
        # calling function  is not providing any values then set is_staff and
        # is_superuser both to False for this user.

        # we want to save the email as lower.
        return self._create_user(email.lower(), password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        #For superuser to login to admin the following three conditions should
        #be satisfied

        # is_staff  => True  (if exit).
        # is_active  => True .
        # is_superuser => True.

        #Set the values if they are not defined

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        #Option1: (Change the values internally irrespective of the user input)
        
        # We want for super user is_staff, is_superuser and is_active to be
        # true. So the below will change the value to True even if someone
        # passes False to any value. But this approach is not good since the
        # user will not know that his values are getting manupulated. 
        

        # extra_fields['is_staff'] = True
        # extra_fields['is_superuser'] = True
        # extra_fields['is_active'] = True

        #Option2:
        
        # Check the values provided, if not True raise exception
        # The below approach is preferred so that the end user knows that he supplied wrong data.


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # what is need for setdefault and again raise error

        # setdefault sets the value only if the key is not already present in the dict. 
        # The caller of the function could still pass extra_fields with some values of id_staff 
        # or is_superuser.

        # What this function does is that while creating a superuser if the calling function 
        # is not providing any values then set is_staff and is_superuser both to True for this user.

        # But, if the values are provided then check if those are True and 
        # raise exceptions otherwise.


        # we want to save the email as lower.
        return self._create_user(email.lower(), password, **extra_fields)


# To have custom fields in the User we have to create a Model which inheret AbscratcUser
# Reason: The auth model contain the User model. Which we cannot modify. So we have to inheret
# AbstractUser class so that we can change it.

# Below we are creating BaseUser Abstract Class from another Abstract class AbstractUser
# Later Below this class we will inheret it in User class

class BaseUser(AbstractUser):
    """User model."""

    # We are inheriting AbstractUser and username is already defined there
    # We dont want to use username as we will be using email as login
    # inorder to not use username we say username = None
    username = None

    #we want to login via otp also without setting password. In that case we
    #want to create a random password
    #overrides password defined in AbstractBaseUser 
    random_string = generateSecureRandomString()
    random_string_hassed = make_password(random_string)
    password=models.CharField(_('password'), max_length=128,default=random_string_hassed)

    # AbstractBaseUser has last_login. But here we are loging via 2 menthods so we need more variables
    recentdate_login_via_passwd = models.DateTimeField(_('last login via password'), blank=True, null=True)
    recentdate_login_via_otp = models.DateTimeField(_('last login via otp'), blank=True, null=True)
    recentdate_password_change = models.DateTimeField(_('last password change'), blank=True, null=True)

    # We are inheriting AbstractUser and first_name and last_name are already defined there
    # We want first_name and last name to be entered compulsory, But in the AbstactUser it
    # says blank=TRUE. So we have to rewrite it so redefine again without blank=True
    first_name = models.CharField(_('first name'), max_length=30,blank=True)
    # NULL allowed, but will never be set as NULL
    # The exception is CharFields and TextFields, which in Django are never saved as NULL. Blank values are stored in the DB as an empty string ('').
    last_name = models.CharField(_('last name'), max_length=150,blank=True)


    # We are inheriting AbstractUser and email is already defined there
    # its defined as blank=TRUE in the AbstractUser.
    # But we will be using it as the login field and also want to be unique
    email = models.EmailField(
        _('email address'),
        help_text="Please Enter valid Email Address",
        unique=True,
        error_messages={
            'unique': _("This email already exists."),
        },
    )

    # We are inheriting AbstractUser and is_active is already defined there
    # We dont want a user to be active unless his email is confirmed
    # we modify it with default=False
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        )
    )

    # NULL allowed, but will never be set as NULL
    # The exception is CharFields and TextFields, which in Django are never saved as NULL. Blank values are stored in the DB as an empty string ('').
    recent_otp_used_for_pass_change = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    date_of_recent_otp_used_for_pass_change = models.DateTimeField(null=True)

    # when we create a login and pass singup form, we try to verify the email then this is required
    otp_used_while_passlogin_create = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    date_of_otp_used_while_passlogin_create = models.DateTimeField(null=True)

    first_otp_used_for_otplogin = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    date_of_first_otp_used_for_otplogin = models.DateTimeField(null=True)


    # List of fields inhereted from AbstractUser
    # is_staff    #'Designates whether the user can log into this admin site.'
    # date_joined

    # List of fields inhereted from AbstractBaseUser
    # password
    # last_login
    # is_active


    # Optional fields to be filled by user for more information
    about = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    

    modified_date = models.DateTimeField(_('modified date'),auto_now=True)

    creation_date = models.DateTimeField(_('creation date'),auto_now_add=True)

    # Because last_login is set by the signal in login() we dont want it and instead have our own
    last_login2 = models.DateTimeField(blank=True, null=True)

    jwt_secret = models.UUIDField(editable=False,default=uuid.uuid4)

    # A string describing the name of the field on the user model that is 
    # used as the unique identifier. This will usually be a username of 
    # some kind, but it can also be an email address, or any other unique 
    # identifier. The field must be unique (i.e., have unique=True set in its 
    # definition), unless you use a custom authentication backend that can 
    # support non-unique usernames.
    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS DEFINITION
    # A list of the field names that will be prompted for when creating a user 
    # via the createsuperuser management command. The user will be prompted to 
    # supply a value for each of these fields. It must include any field for which 
    # blank is False or undefined and may include additional fields you want prompted 
    # for when a user is created interactively. REQUIRED_FIELDS has no effect in other 
    # parts of Django, like creating a user in the admin.

    # presently we dont want to be asked for anything while createsuperuser
    REQUIRED_FIELDS = []

    class Meta:
        """Define Meta class for BaseUser model."""
        # We want this class to be abstract so we define the below
        abstract = True 

    # def jwt_get_secret_key(self):
    #     return self.jwt_secret



# Finally Inheret BaseUser class (Why we are using this way is to have flexibility later)
# This how the actual /venv_btg/lib/python3.6/site-packages/django/contrib/auth/models.py is done
# Ofcouse there is no need to do this but we just keep it like the /auth/models.py say

class User(BaseUser):
    objects = UserManager()

    # the below Meta class is added in /venv_btg/lib/python3.6/site-packages/django/contrib/auth/models.py
    # User model

    class Meta(BaseUser.Meta):
        swappable = 'AUTH_USER_MODEL'




from django.contrib.auth import get_user_model

def get_sentinel_user():
    try:
        match = get_user_model().objects.get(email='deleted')
    except:
        match = get_user_model().objects.create(email='deleted',last_login2=timezone.now())
    return match

class ActionTypeForUserSessionLog(models.Model):
    action = models.CharField(max_length=100, blank=False,unique=True)

class UserSessionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user))
    user_email =    models.EmailField()
    otp_used_for_pass_change = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    otp_used_while_passlogin_create = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    otp_used_for_otplogin = models.CharField(
        _('otp'),
        help_text="Please Enter valid OTP sent to your Email",
        max_length=6,
        validators=[
            RegexValidator(
                r'^\d{6}$',
                message=_('OTP shoud be of 6 digits'),
                code='invalid'
            )
        ]
    )

    device_type = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    created_time = models.DateTimeField(default=timezone.now)
    action_type = models.ForeignKey(ActionTypeForUserSessionLog, on_delete=models.PROTECT)
    unique_id = models.UUIDField(editable=False,default=uuid.uuid4)
    jwt_secret = models.UUIDField(editable=False,default=uuid.uuid4)






#We have to pass initial data to ActionTypeForUserSessionLog model:
#https://docs.djangoproject.com/en/2.2/howto/initial-data/#providing-data-with-fixtures
#Create a fixtures folder in any app and then name it something then do
# manage.py loaddata something.

#You’ll store this data in a fixtures directory inside your app.

#Loading data is easy: just call manage.py loaddata <fixturename>, where
#<fixturename> is the name of the fixture file you’ve created. Each time you run
#loaddata, the data will be read from the fixture and re-loaded into the
#database. Note this means that if you change one of the rows created by a
#fixture and then run loaddata again, you’ll wipe out any changes you’ve made.



###    [
###      {
###        "model": "custom_user.ActionTypeForUserSessionLog",
###        "pk": 1,
###        "fields": {
###          "action": "pass_change",
###        }
###      },
###      {
###        "model": "custom_user.ActionTypeForUserSessionLog",
###        "pk": 2,
###        "fields": {
###          "action": "login_by_otp",
###        }
###      },
###      {
###        "model": "custom_user.ActionTypeForUserSessionLog",
###        "pk": 3,
###        "fields": {
###          "action": "login_by_pass",
###        }
###      },
###      {
###        "model": "custom_user.ActionTypeForUserSessionLog",
###        "pk": 4,
###        "fields": {
###          "action": "passlogin_email_validation",
###        }
###      }
###    ]