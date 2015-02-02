from django.shortcuts import render_to_response
# Create your views here.

def index(request):
    return render_to_response('base.html')

def contact(request):
    return render_to_response('contact.html')

def database(request):
    return render_to_response('database.html')