"""basic_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # this view is for testing 7commit related i.e sql logging, pretty printing, traceback 
    path('test7commit',views.test_7commit, name='test_7commit'),
    # this view is for testing 8commit related i.e sending email by gmail smtp
    path('test8commit',views.test_8commit, name='test_8commit'),
    # this view is for testing celery related by sending email
    path('celery_example_5commit',views.celery_example_5commit, name='celery_example_5commit'),
    # include all the urls from articles app
    path('', include('articles.urls',namespace='articles_namespace')),
    # include all the urls from login_register_password
    path('login_register_password/', include('login_register_password.urls',namespace='login_register_password_namespace')),
    # webpack_and reactjs_example
    path('polls_webpack_react_example/', include('polls_example_for_webpack_and_reactjs.polls.urls'))
]
