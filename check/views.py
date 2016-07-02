from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render
from django.http import HttpResponse
import activity_check
# Create your views here.
# add to the top
from forms import MemberList

# add to your views
def check(request):
    form_class = MemberList
    
    if request.method == 'POST':
        form = form_class(data=request.POST)
        
        if form.is_valid():
            year_and_month = request.POST.get('year_and_month', '')
            member_list = request.POST.get('member_list', '')
            
            activities = activity_check.checkActivity(year_and_month, member_list)
            
            return HttpResponse(activities)
    
    return render(request, 'check/actcheck.html', {
        'form': form_class,
    })
