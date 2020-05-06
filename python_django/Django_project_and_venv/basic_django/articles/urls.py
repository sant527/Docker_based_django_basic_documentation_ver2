from django.urls import path
from . import views

app_name='articles_app_name'

urlpatterns = [
    path('',views.articles, name='articles'),
]