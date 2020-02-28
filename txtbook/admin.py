from django.contrib import admin
from .models import TextbookPost
from .models import Textbook
# Register your models here.

class textbookpost_admin(admin.ModelAdmin):
    list_display = ('textbook', 'date_published')

admin.site.register(TextbookPost,textbookpost_admin)

class textbook_admin(admin.ModelAdmin):
    list_display = ('title','author','dept','classnum','sect')


admin.site.register(Textbook,textbook_admin)
