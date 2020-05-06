from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages

## LOGGING
import logging
import traceback
logger_custom_string = logging.getLogger("custom_string")
from basic_django import settings as settings_basic_django

# Create your views here.

def articles(request):
    logger_custom_string.debug(settings_basic_django.pp_odir(locals(),traceback.format_stack()))
    return render(request, 'articles/main_page/articles.html')