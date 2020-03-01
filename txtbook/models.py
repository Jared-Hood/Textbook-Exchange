import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class Textbook(models.Model):
    title = models.CharField(max_length=200, default='N/A')
    author = models.CharField(max_length=200, default='N/A',)
    dept = models.CharField(max_length=100, default='N/A', blank=True)
    classnum = models.CharField(max_length=100, default='N/A', blank=True)
    sect = models.CharField(max_length=100, default='N/A', blank=True)
    isbn = models.CharField(max_length=100, default='N/A', blank=True)
    new_price_bookstore = models.CharField(max_length=100, default='0.0', blank=True)
    used_price_bookstore = models.CharField(max_length=100, default='0.0', blank=True)
    amazon_link = models.CharField(max_length=1000, default='N/A', blank=True)
    user_created = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('txtbook:post', kwargs={'pk': self.id})

class TextbookPost(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.DO_NOTHING, null=True)
    price = models.CharField(max_length=100, default='0.0')
    negotiable = models.CharField(max_length=100, default='Yes')
    exchangable = models.CharField(max_length=100, default='Yes')
    max_diff = models.CharField(max_length=100, default='0.0',blank=True)
    payment = models.CharField(max_length=200, default='Venmo')
    condition = models.CharField(max_length=100, default='5')
    additional_info = models.TextField(max_length=10000, default='N/A',blank=True)
    date_published = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=200, default='N/A')
    image = models.ImageField(upload_to='images', blank=True)

    def __str__(self):
        return str(self.id) + ' ' + self.textbook.title

    def get_absolute_url(self):
        return reverse('txtbook:post',kwargs={'pk':self.id})
