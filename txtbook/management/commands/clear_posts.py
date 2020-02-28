from django.core.management.base import BaseCommand
from txtbook.models import Textbook, TextbookPost


class Command(BaseCommand):
    def handle(self, *args,**options):
        TextbookPost.objects.all().delete()
