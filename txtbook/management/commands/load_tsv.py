import csv
from txtbook.models import Textbook, TextbookPost, User, Profile

with open('/testbook_list.tsv') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        book = Textbook.objects.create(dept=row[0], classnum=row[1], sect=1, isbn=row[6], title=row[4], author=row[3], user_created=False)
        book.save()