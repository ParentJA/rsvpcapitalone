__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Django imports...
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def home(request):
    return render(request, 'home.html')