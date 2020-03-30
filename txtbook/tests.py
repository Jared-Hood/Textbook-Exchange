from django.test import TestCase
from .models import TextbookPost
from .models import Textbook
from django.urls import reverse

# Create your tests here.

#Test textbook objects
class TextbookTests(TestCase):
    def setUp(self):
        t1 = Textbook(title="Homegoing", author="Gyasi, Yaa", dept="AAS", classnum="3500", sect="GHANA",
                      isbn="978-1-101-97106-2")
        t2 = Textbook(title="Computers", author='Hood, Jared', isbn='1234')
        t3 = Textbook(title="Spanish", author="Escobar, Pablo",
                      amazon_link="https://www.amazon.com/Spanish-Grammar-Beginners-complete-textbook/dp/1698838506/ref=sr_1_1_sspa?crid=2K5A0NP01M0SD&keywords=spanish+textbook&qid=1585530229&sprefix=Spanish+te%2Caps%2C182&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzTzhGVkxCSVYwUTYyJmVuY3J5cHRlZElkPUEwNTEyMTE5MTBNMFhaREZTNkUzUCZlbmNyeXB0ZWRBZElkPUEwOTY0MDgzVDJYSkJDQkhRSzhDJndpZGdldE5hbWU9c3BfYXRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ==")
        t1.save()
        t2.save()
        t3.save()

    def test_textbooks_title(self):
        book = Textbook.objects.get(title='Homegoing')
        self.assertEqual(book.author, "Gyasi, Yaa")
        book2 = Textbook.objects.filter(title='Not here')
        self.assertEqual(len(book2),0)

    def test_textbooks_default(self):
        books = Textbook.objects.filter(dept='N/A')
        all_books = Textbook.objects.all()
        self.assertEqual(len(books),2)
        books_none = Textbook.objects.exclude(dept='N/A')
        self.assertEqual(len(books_none),1)
        self.assertTrue(len(books_none) + len(books) == len(all_books))



# E3_test1
# Tests the textbookpost model, and our database
# Creates a listing for a textbook (first in the database)
# and checks to see if it is in the database.
class TextbookPostTests(TestCase):
    def setUp(self):
        t1 = Textbook(title="Homegoing", author="Gyasi, Yaa", dept="AAS", classnum="3500", sect="GHANA", isbn="978-1-101-97106-2")
        t2 = Textbook(title="Computers", author='Hood, Jared', isbn='1234')
        t3 = Textbook(title="Spanish", author="Escobar, Pablo", amazon_link="https://www.amazon.com/Spanish-Grammar-Beginners-complete-textbook/dp/1698838506/ref=sr_1_1_sspa?crid=2K5A0NP01M0SD&keywords=spanish+textbook&qid=1585530229&sprefix=Spanish+te%2Caps%2C182&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEzTzhGVkxCSVYwUTYyJmVuY3J5cHRlZElkPUEwNTEyMTE5MTBNMFhaREZTNkUzUCZlbmNyeXB0ZWRBZElkPUEwOTY0MDgzVDJYSkJDQkhRSzhDJndpZGdldE5hbWU9c3BfYXRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ==")
        t1.save()
        t2.save()
        t3.save()
        tp1 = TextbookPost( textbook = t1, condition=5, price='10.00' )
        tp2 = TextbookPost(textbook = t2, condition=3, price='5.00')
        tp3 = TextbookPost(textbook = t3, condition=2, price='5.00', format='text')
        tp1.save()
        tp2.save()
        tp3.save()

    def test_check_listings(self):
        #Check number of listings
        listings = TextbookPost.objects.all()
        self.assertEqual(len(listings),3)

    def test_check_listing_price(self):
        listing = TextbookPost.objects.get(price='10.00')
        self.assertEqual(listing.textbook.author, "Gyasi, Yaa")

        listing_set = TextbookPost.objects.filter(price='5.00')
        listing_post = listing_set.get(condition=3)
        listing_post_2 = listing_set.get(condition=2)
        listing_book = listing_post.textbook
        listing_book_2 = listing_post_2.textbook
        self.assertEqual(len(listing_set),2)
        self.assertEqual(listing_post.condition, '3')
        self.assertEqual(listing_book.title, 'Computers')
        self.assertEqual(listing_post_2.condition, '2')
        self.assertEqual(listing_book_2.title, 'Spanish')

    def test_check_listing_defaults(self):
        listing = TextbookPost.objects.exclude(format='N/A')
        listing_default_payment = TextbookPost.objects.filter(payment='Venmo')
        listing_include = TextbookPost.objects.filter(format='N/A')
        book = listing.get(format='text').textbook
        self.assertEqual(book.title, 'Spanish')
        self.assertEqual(len(listing_include),2)
        self.assertEqual(len(listing_default_payment),3)

#Test PostsView
class PostViewTest(TestCase):
    """
    Test before adding any textbook posts
    """
    def test_no_books(self):
        response = self.client.get(reverse('txtbook:allPosts'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_post_list'], [])
        self.assertContains(response, "No posts are available.")

    """
    Test after adding a post
    """
    def test_books(self):
        t1 = Textbook(title="Homegoing", author="Gyasi, Yaa", dept="AAS", classnum="3500", sect="GHANA", isbn="978-1-101-97106-2")
        t1.save()
        tp1 = TextbookPost(textbook=t1, condition=5, price='10.00')
        tp1.save()

        response = self.client.get(reverse('txtbook:allPosts'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_post_list'], ['<TextbookPost: 1 Homegoing>'])
        self.assertTrue(response != "No posts are available.")


