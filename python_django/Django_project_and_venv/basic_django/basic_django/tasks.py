###############################
## LOGGING
import logging
logger_custom_string = logging.getLogger("custom_string")
from basic_django import settings
#usage:
#logger_custom_string.debug("ANY STRING")
#logger_custom_string.debug(settings.pp_odir(user_set))  # This will pretty print all the properties from dir(user_set)
#logger_custom_string.debug(settings.pp_dict(user_set.__dict__))  # This will pretty print any dictionary
#sql = str(user_set.query)
#sql = user_set.query.__str__()
#logger_custom_string.debug(settings.pp_sql_sql(sql)) # pretty print the sql obtained from the .query
#logger_custom_string.debug(settings.pp_sql_query_pg(user_set)) # pretty print the sql using mogrify only possible with Psycopg
#logger_custom_string.debug(settings.pp_sql_query_any(user_set)) # pretty print the sql using EXPLAIN. But runs extra sql
logger_database = logging.getLogger("django.db.backends")
#usage:
#logger_database.filters[0].open()
#logger_database.filters[0].close()


#Note tasks can be declared anywhere. It has to lie in the INSTALLED APPS.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basic_django.settings') does the magic
#this will help celery to find all the tasks.

from basic_django import celery_app
from django.core.mail import send_mail

@celery_app.task
def send_email_task(recipient_list,subject,message,):
    send_mail(subject, message,None,[recipient_list])
    logger_custom_string.debug("Email Sent")
