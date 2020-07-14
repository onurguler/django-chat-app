from django.shortcuts import render, HttpResponse

# Create your views here.

def signup(request):
    return HttpResponse("<h1>Signup View</h1>")
