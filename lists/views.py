from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from lists.models import Item

# Create your views here.
def home_page(request:HttpRequest,)->HttpResponse:
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')

    return render(request, 'home.html')