'''
Created on Jun 30, 2016

@author: Cog Vokan
'''
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.check, name='check'),
]
