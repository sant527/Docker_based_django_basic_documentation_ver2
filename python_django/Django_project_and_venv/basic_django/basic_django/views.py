from basic_django import settings
from django.http import HttpResponse
from .tasks import send_email_task
from custom_user.models import User
from django.http import HttpResponse
import datetime
from . import settings
from django.db import connections
import json
import logging

def test_8commit(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.TESTING_EMAIL,]
    from django.core.mail import send_mail
    send_mail( subject, message, email_from, recipient_list )
    html = "<html><body>Email sent</body></html>"
    return HttpResponse(html)


def celery_example_5commit(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [settings.TESTING_EMAIL,]
    from django.core.mail import send_mail
    # USING CELERY TASK for sending email Asynchronously
    #match.email_user(subject, message). This will delay the response 
    # So will do this task asynchronously using celery
    # We have created a celery task. Using it we will send the email.
    # The code does not have to wait till the email is sent
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    recipient_list = [settings.TESTING_EMAIL,]
    send_email_task.delay(recipient_list,subject,message)
    html = "<html><body>Email sent using celery</body></html>"
    return HttpResponse(html)


logger_custom_string = logging.getLogger("custom_string")
logger_database = logging.getLogger("django.db.backends")


# We are going to test logging, pretty printing and traceback and also querycount
def test_7commit(request):

    logger_database.filters[0].open()
    #we allow the database log from here

    from django import db
    user_set = User.objects.all() # here sql is executed and it will be shown in the console

    for user in user_set:
        pass

    #we block the database log from here
    logger_database.filters[0].close()

    from django import db
    user_set = User.objects.all() # here sql is executed and but it will be shown in the console

    for user in user_set:
        pass

    # checking the functions for pretty priting
    logger_custom_string.debug(settings.pp_odir(user_set))  # This will pretty print all the properties from dir(user_set)
    logger_custom_string.debug(settings.pp_dict(user_set.__dict__))  # This will pretty print any dictionary
    sql = str(user_set.query)
    sql = user_set.query.__str__()
    logger_custom_string.debug(settings.pp_sql_sql(sql)) # pretty print the sql obtained from the .query
    logger_custom_string.debug(settings.pp_sql_query_pg(user_set)) # pretty print the sql using mogrify only possible with Psycopg
    logger_custom_string.debug(settings.pp_sql_query_any(user_set)) # pretty print the sql using EXPLAIN. But runs extra sql


    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    import traceback
    logger_custom_string.debug(settings.pp_traceback(traceback.format_stack())) #test traceback
    return HttpResponse(html)