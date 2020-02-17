# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader


def index(request):
    return render(request, 'txtbook/index.html')

def addTextbook(request):
    return render(request, 'txtbook/addTextbook.html')