# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse,HttpRequest
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
from urllib.parse import urlencode
import csv, io
from django.shortcuts import redirect
from .models import Textbook, TextbookPost, User, Profile
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.shortcuts import redirect


# Homepage
def index(request):
    return render(request, 'txtbook/bootstrap-landing.html')


def text(request, pk):
    return render(request, 'txtbook/text.html', {'textbook': Textbook.objects.get(id=pk)})


def logout_request(request):
    logout(request) # logout the user
    return HttpResponseRedirect("/")


def textView(request):
    all_text = Textbook.objects.all()
    paginator = Paginator(all_text, 20)
    page = request.GET.get('page',1)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    index = books.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]
    return render(request,'txtbook/textlist.html', {'books': books, 'page_range':page_range})


# Lists all Posts
class allPostsView(generic.ListView):
    template_name = 'txtbook/allPosts.html'
    context_object_name = 'latest_post_list'

    def get_queryset(self):
        """
        Return all posts, ordered by most recent publish date.
        """
        return TextbookPost.objects.filter(
            date_published__lte=timezone.now()
        ).order_by('-date_published')


# Shows a post individually
class PostView(generic.DetailView):
    model = TextbookPost
    template_name = 'txtbook/post.html'
    context = TextbookPost

    def get_queryset(self):
        """
        Excludes any posts that aren't published yet.
        """
        return TextbookPost.objects.filter(date_published__lte=timezone.now())


def contactSeller(request, pk):
    template_name = 'txtbook/contactSeller.html'
    post = TextbookPost.objects.get(pk=pk)

    return render(request, template_name, {'textbookpost': post})


def sendEmail(request, pk):

    subject = request.POST['subject']
    Message = request.POST['message']
    from_email = request.POST['from_email']
    to_email = request.POST['to_email']

    post = TextbookPost.objects.get(pk=pk)

    send_mail(
        subject,
        Message,
        from_email,
        [to_email],
        fail_silently=False,
    )

    messageSent = True

    return render(request, "txtbook/emailSent.html", {"messageSent" : messageSent, "pk" : pk, 'textbookpost': post})


def search_posts_by_book(request, pk):
    results = []
    results = TextbookPost.objects.filter(Q(textbook__id=pk)).order_by('date_published','-email')
    paginator = Paginator(results, 20)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    index = posts.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]
    return render(request,'txtbook/post_results.html', {'posts': posts, 'page_range':page_range, 'search_term':Textbook.objects.get(id=pk)})


# The function that is called when the search bar is used to search through posts.
def search_posts(request):
    template = 'txtbook/addTextbook.html'
    query = request.GET.get('q')
    results = []
    results = TextbookPost.objects.filter(Q(textbook__title__icontains=query)| Q(textbook__author__icontains=query)|Q(email__icontains=query)).distinct('email')
    paginator = Paginator(results, 20)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    index = posts.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]
    return render(request,'txtbook/search_results.html', {'posts': posts, 'page_range':page_range, 'search_term':query})


# The function that is called when the search bar is used on the addTextbook page.
def search(request):
    template = 'txtbook/addTextbook.html'
    query = request.GET.get('q')
    query_numeric=""
    results = []
    if query:
        if(query[0].isnumeric()):
            for char in query:
                if not char.isnumeric():
                    continue
                else:
                    query_numeric += char
        if(query_numeric.isnumeric()):
            results = Textbook.objects.filter(Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query_numeric)).distinct('isbn','title').order_by('title','-isbn').distinct('title')
        else:
            print("not numeric")
            results = Textbook.objects.filter(Q(title__icontains=query)| Q(author__icontains=query)).distinct('isbn','title').distinct('isbn','title').order_by('title','-isbn').distinct('title')
    paginator = Paginator(results, 20)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
    index = books.number - 1
    max_index = len(paginator.page_range)
    start_index = index - 5 if index >= 5 else 0
    end_index = index + 5 if index <= max_index - 5 else max_index
    page_range = paginator.page_range[start_index:end_index]
    return render(request,'txtbook/search_results.html', {'books': books, 'page_range':page_range, 'search_term':query})


# an intermediary function that allows addExistingTextbook to utilize context
def transfer(request,pk):
    current = Textbook.objects.get(id=pk)
    return render(request,'txtbook/addExistingTextbook.html', {'textbook': current})


# The function which is called when 'post' is clicked on a add existing textbook page.
# Should redirect to
def addExistingTextbook(request,pk):
    try:
        new_price = request.POST['price']
        new_negotiable = request.POST['negotiable']
        new_exchangable = request.POST['exchangable']
        new_maxdiff = request.POST['maxDiff']
        new_payment = request.POST['payment']
        new_condition = request.POST['inlineRadioOptions']
        new_additional_info = request.POST['additionalInfo']
        new_format = request.POST['format']
        new_image = request.FILES.get('image', False)
        new_email = request.POST['email']
        profile_id = request.POST['profile']

        if (new_price == ''):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Your posting MUST have a price."})

        if (new_email == ''):
            return render(request, 'txtbook/addExistingTextbook.html',
                          {'textbook': Textbook.objects.get(id=pk), 'error_message': "You must be logged in to post a textbook."})

    except (KeyError, TextbookPost.DoesNotExist):
        return render(request, 'txtbook/addExistingTextbook.html', {
            # 'error_message': "One or more of the fields is empty."
        })
    else:
        tp = TextbookPost(
            textbook=Textbook.objects.get(id=pk),
            price=float(new_price),
            negotiable=new_negotiable,
            exchangable=new_exchangable,
            max_diff=new_maxdiff,
            payment=new_payment,
            condition=new_condition,
            additional_info=new_additional_info,
            format=new_format,
            date_published=timezone.now(),
            image=new_image,
            email=new_email,
            profile=Profile.objects.get(id=profile_id),
        )
        tp.save()
        return HttpResponseRedirect(tp.get_absolute_url())
    # return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk)})


# Main page to add a textbook.
def addTextbook(request):
        try:
            new_title = request.POST['title']
            new_author = request.POST['author']
            new_dept = request.POST['dept']
            new_classnum = request.POST['classnum']
            new_isbn = request.POST['isbn']
            new_sect = request.POST['sect']
            new_price = request.POST['price']
            new_negotiable = request.POST['negotiable']
            new_exchangable = request.POST['exchangable']
            new_maxdiff = request.POST['maxDiff']
            new_payment = request.POST['payment']
            new_condition = request.POST['inlineRadioOptions']
            new_additional_info = request.POST['additionalInfo']
            new_format = request.POST['format']
            new_image = request.FILES.get('image', False)
            new_email = request.POST['email']
            profile_id = request.POST['profile']

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
                })

            if (new_email == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "You must be logged in to post a textbook"
                })


        except (KeyError, TextbookPost.DoesNotExist):
            return render(request, 'txtbook/addTextbook.html', {
                # 'error_message': "One or more of the fields is empty."
            })

        else:

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
                })

            if (new_email == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "You must be logged in to post a textbook"
                })

            book = Textbook.objects.create(title=new_title, author=new_author, dept=new_dept, classnum=new_classnum,
                                           sect=new_sect, isbn=new_isbn, user_created=True)
            book.save()
            tp = TextbookPost(
                textbook=book,
                price=float(new_price),
                negotiable=new_negotiable,
                exchangable=new_exchangable,
                max_diff=new_maxdiff,
                payment=new_payment,
                condition=new_condition,
                additional_info=new_additional_info,
                format=new_format,
                date_published=timezone.now(),
                image=new_image,
                email=new_email,
                profile=Profile.objects.get(id=profile_id),

            )
            tp.save()

            return HttpResponseRedirect(tp.get_absolute_url())


# The view function to upload a database to the mysite
# TODO: add admin protection to the url.
def textbook_upload(request):
    template = "txtbook/textbook_upload.html"
    prompt = {
        'order' : 'Order of the TSV should be dept, course nbr, sect, instructor (ignore), title, isbn, new price, used price, and then amazon link'
    }
    if request.method == "GET":
        return render(request, template, prompt)
    tsv_file = request.FILES['file']
    if not tsv_file.name.endswith('.tsv'):
        message.error(request,'This is not a tsv file')
    data_set = tsv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    for column in csv.reader(io_string, delimiter='\t'):
        if(column[4] == ""):
            continue
        created = Textbook.objects.create(
            dept=column[0],classnum=column[1],sect=column[2],title=column[4],author=column[5],isbn=column[6], new_price_bookstore=column[7],used_price_bookstore=column[8],amazon_link=column[9]
        )
    context = {}
    return render(request,template,context)


def filtered_posts_search(request):
    template = "txtbook/allPosts.html"
    model = TextbookPost
    context = TextbookPost

    sort_date = request.POST['inlineRadioOptions']
    max_price = request.POST['max_price']

    if sort_date == 'newest':
        latest_post_list = TextbookPost.objects.filter(date_published__lte=timezone.now()).order_by('-date_published')
    else:
        latest_post_list = TextbookPost.objects.filter(date_published__lte=timezone.now()).order_by('date_published')

    if max_price != '':
        latest_post_list = latest_post_list.filter(price__lte=float(max_price))

    return render(request, 'txtbook/filtered_posts_search.html',
                  {'latest_post_list': latest_post_list, 'max_price': max_price, 'sort_date': sort_date})


# def profile_page(request, pk):
#     model = User
#     context = User
#     template = "txtbook/profile_page.html"
#
#     textbook_posts = User.textbookpost_set.all()
#     user_profile = Profile.objects.get(id=pk)
#
#     return render(request, 'txtbook/profile_page.html',
#                   {'textbook_posts': textbook_posts, 'profile': user_profile})


# Code to get the ForeignKey set for an object:
# https://stackoverflow.com/questions/51950416/reversemanytoonedescriptor-object-has-no-attribute-all/51950693
class profile_page(generic.DetailView):
    template_name = 'txtbook/profile_page.html'
    model = Profile
    # textbook_posts = User.textbookpost_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['textbook_posts'] = instance.textbookpost_set.all()
        return context


def create_profile(request):
    try:
        new_email = request.POST['email']
        new_name = request.POST['name']
        new_venmo = request.POST['venmo']
        new_year = request.POST['year']
        new_major = request.POST['major']
        new_bio = request.POST['bio']
        new_phone = request.POST['phone']
        user_id = request.POST['user']

        if (new_name == ''):
            return render(request, 'txtbook/create_profile.html', {
                'error_message': "You MUST fill out a name."
            })


    except (KeyError, Profile.DoesNotExist):
        return render(request, 'txtbook/create_profile.html', {
            # 'error_message': "One or more of the fields is empty."
        })

    else:

        if (new_name == ''):
            return render(request, 'txtbook/create_profile.html', {
                'error_message': "You MUST fill out a name."
            })

        p = Profile(
            user=User.objects.get(id=user_id),
            email=new_email,
            name=new_name,
            venmo=new_venmo,
            year=new_year,
            major=new_major,
            bio=new_bio,
            phone=new_phone,
        )
        p.save()
        return HttpResponseRedirect(p.get_absolute_url())


def edit_profile(request, pk):
    try:
        new_name = request.POST['name']
        new_venmo = request.POST['venmo']
        new_year = request.POST['year']
        new_major = request.POST['major']
        new_bio = request.POST['bio']
        new_phone = request.POST['phone']
        user_id = request.POST['user']

        if (new_name == ''):
            return render(request, 'txtbook/edit_profile.html', {
                'profile': Profile.objects.get(id=pk),
                'error_message': "You MUST fill out a name."
            })


    except (KeyError, Profile.DoesNotExist):
        return render(request, 'txtbook/edit_profile.html', {
            'profile': Profile.objects.get(id=pk),
        })

    else:

        if (new_name == ''):
            return render(request, 'txtbook/edit_profile.html', {
                'profile': Profile.objects.get(id=pk),
                'error_message': "You MUST fill out a name."
            })

        p = Profile.objects.get(id=pk)

        p.name = new_name
        p.venmo = new_venmo
        p.year = new_year
        p.major = new_major
        p.bio = new_bio
        p.phone = new_phone

        p.save()

        return HttpResponseRedirect(p.get_absolute_url())


def edit_post(request, pk):
    try:

        new_title = request.POST['title']
        new_author = request.POST['author']
        new_dept = request.POST['dept']
        new_classnum = request.POST['classnum']
        new_isbn = request.POST['isbn']
        new_sect = request.POST['sect']

        new_price = request.POST['price']
        new_negotiable = request.POST['negotiable']
        new_exchangable = request.POST['exchangable']
        new_maxdiff = request.POST['maxDiff']
        new_payment = request.POST['payment']
        new_condition = request.POST['inlineRadioOptions']
        new_additional_info = request.POST['additionalInfo']
        new_format = request.POST['format']
        # new_image = request.FILES.get('image', False)

        tp = TextbookPost.objects.get(id=pk)

        if (tp.textbook.user_created) and (new_title == '' or new_price == ''):
            return render(request, 'txtbook/edit_post.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Your textbook MUST have a title and price."
            })

        if (new_price == ''):
            return render(request, 'txtbook/edit_post.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

    except (KeyError, Profile.DoesNotExist):
        return render(request, 'txtbook/edit_post.html', {
            'textbookpost': TextbookPost.objects.get(id=pk),
        })

    else:

        if (tp.textbook.user_created) and (new_title == '' or new_price == ''):
            return render(request, 'txtbook/edit_post.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Your textbook MUST have a title and price."
            })

        if (new_price == ''):
            return render(request, 'txtbook/edit_post.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

        tp.price = new_price
        tp.negotiable = new_negotiable
        tp.exchangable = new_exchangable
        tp.max_diff = new_maxdiff
        tp.payment = new_payment
        tp.condition = new_condition
        tp.additional_info = new_additional_info
        tp.format = new_format
        # tp.image = new_image
        tp.date_published = timezone.now()

        if tp.textbook.user_created == True:
            tp.textbook.title = new_title
            tp.textbook.author = new_author
            tp.textbook.dept = new_dept
            tp.textbook.classnum = new_classnum
            tp.textbook.isbn = new_isbn
            tp.textbook.sect = new_sect

        tp.save()

        return HttpResponseRedirect(tp.get_absolute_url())
