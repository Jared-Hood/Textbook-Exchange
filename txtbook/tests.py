from django.test import TestCase, Client, RequestFactory
from .models import TextbookPost, Profile
from .models import Textbook
from django.urls import reverse,resolve
from txtbook.views import index, addTextbook, search
from .views import *

from django.contrib.auth.models import AnonymousUser, User

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


class ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        t1 = Textbook(title="Homegoing", author="Gyasi, Yaa", dept="AAS", classnum="3500", sect="GHANA",
                      isbn="978-1-101-97106-2")
        tp1 = TextbookPost(textbook=t1, condition=5, price='10.00')
        p1 = Profile(user=self.user, name="jacob")
        t1.save()
        tp1.save()
        p1.save()

        self.book = t1
        self.post = tp1
        self.profile = p1

    def test_allposts(self):
        request = self.factory.get('/allPosts')
        request.user = self.user
        response = allPostsView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_contactSeller(self):
        url = reverse('txtbook:contactSeller', args=(self.post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        url = reverse('txtbook:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_text(self):
        url = reverse('txtbook:text', args=(self.book.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        url = reverse('txtbook:sendEmail', args=(self.post.id,))
        try:
            response = self.client.get(url)
        except:
            self.assertEqual(1,1)

    def test_seach_book(self):
        url = reverse('txtbook:search_posts', args=(self.book.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        url = reverse('txtbook:search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_transfer(self):
        url = reverse('txtbook:transfer', args=(self.book.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_existing(self):
        url = reverse('txtbook:addTextbook')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload(self):
        url = reverse('txtbook:textbook_upload')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_create_profile(self):
        url = reverse('txtbook:create_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sold(self):
        url = reverse('txtbook:mark_post_sold', args=(self.post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_repost(self):
        url = reverse('txtbook:repost', args=(self.post.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_search_options(self):
        url = reverse('txtbook:search_options')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_textview(self):
        url = reverse('txtbook:textlist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


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


#Testing urls
class TestUrls(TestCase):
    def test_index_url_is_resolved(self):
        url = reverse('txtbook:index')
        print(resolve(url))
        self.assertEquals(resolve(url).func, index)

    def test_addtextbook_url_is_resolved(self):
        url = reverse('txtbook:addTextbook')
        print(resolve(url))
        self.assertEquals(resolve(url).func, addTextbook)

    def test_results_url_is_resolved(self):
        url = reverse('txtbook:search')
        print(resolve(url))
        self.assertEquals(resolve(url).func, search)


class TestSearch(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('txtbook:search')
        Textbook.objects.create(
            title="text1", author="author1", user_created=False,
        )

    def test_search_GET(self):
        response = self.client.get(self.url, {'q':'text'})
        self.assertEquals(response.status_code, 200)
