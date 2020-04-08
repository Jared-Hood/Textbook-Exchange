import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


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

# Django documentation on User models: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, default=NULL)
#     name = models.CharField(max_length=200, default='')
#     email = models.CharField(max_length=100, default='')
#     rating = models.CharField(max_length=100, default='')
#     posts = models.ForeignKey(TextbookPost, on_delete=models.CASCADE, null=True)
#     venmo = models.CharField(max_length=100, default='')
#
#     def __str__(self):
#         return str(self.id) + ' ' + str(self.email)
#
#     def get_absolute_url(self):
#         return reverse('txtbook:profile_page', kwargs={'pk': self.id})
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance, email=user.email)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_constraint=False)
    name = models.CharField(max_length=200, default='')
    email = models.CharField(max_length=100, default='')
    # posts = models.ManyToManyField(TextbookPost, blank=True)
    # post_ids = ArrayField(
    #     base_field=models.IntegerField(), blank=True, null=True
    # )
    rating = models.CharField(max_length=100, default='',blank=True)
    venmo = models.CharField(max_length=100, default='',blank=True)
    year = models.CharField(max_length=100, default='',blank=True)
    major = models.CharField(max_length=100, default='', blank=True)
    phone = models.CharField(max_length=100, default='', blank=True)
    bio = models.TextField(max_length=10000, default='',blank=True)

    def get_absolute_url(self):
        return reverse('txtbook:profile_page',kwargs={'pk':self.id})


# Django Documentation for manyToOne fields (AKA ForeignKey fields):
# https://docs.djangoproject.com/en/3.0/topics/db/examples/many_to_one/
# Code describing ForeignKey relationship in another example:
# https://stackoverflow.com/questions/14663523/foreign-key-django-model
class TextbookPost(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.DO_NOTHING, null=True)
    price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    email = models.CharField(max_length=100, default='')
    # user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
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