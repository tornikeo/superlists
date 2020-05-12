from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.
def home_page(request:HttpRequest,)->HttpResponse:
    return render(request, 'home.html', {
        'new_item_text':request.POST.get('item_text',''),
    })
