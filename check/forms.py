'''
Created on Jun 30, 2016

@author: Cog Vokan
'''
from django import forms

class MemberList(forms.Form):
    year_and_month = forms.CharField(required = True)
    member_list = forms.CharField(
        required = True,
        widget = forms.Textarea
    )