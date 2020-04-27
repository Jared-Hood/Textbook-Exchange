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
from django.template.context import RequestContext
from django.shortcuts import redirect
from django import template


# Homepage
def index(request):
    user = request.user
    if user.is_anonymous == False:
        try:
            if user.profile.id == '':
                return render(request, 'txtbook/create_profile.html')
        except:
            return render(request, 'txtbook/create_profile.html')

    return render(request, 'txtbook/bootstrap-landing.html')


def homepage(request):
    return render(request, 'txtbook/bootstrap-landing.html')


def text(request, pk):
    return render(request, 'txtbook/text.html', {'textbook': Textbook.objects.get(id=pk)})

def logout_request(request):
    logout(request) # logout the user
    return HttpResponseRedirect("/")


def textView(request):
    all_text = Textbook.objects.all().order_by('dept','classnum')
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
            date_published__lte=timezone.now(), sold=False,
        ).order_by('-date_published')


# def allPosts(request):
#     template = "txtbook/allPosts.html"
#     model = TextbookPost
#     context = TextbookPost
#
#     results = TextbookPost.objects.filter(
#             date_published__lte=timezone.now(), sold=False,
#         ).order_by('-date_published')
#
#     paginator = Paginator(results, 20)
#     page_request_var = 'page'
#     page = request.GET.get(page_request_var)
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     index = posts.number - 1
#     max_index = len(paginator.page_range)
#     start_index = index - 5 if index >= 5 else 0
#     end_index = index + 5 if index <= max_index - 5 else max_index
#     page_range = paginator.page_range[start_index:end_index]
#
#     return render(request, 'txtbook/allPosts.html',
#                   {'latest_post_list': posts})


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
    book = post.textbook

    return render(request, template_name, {'textbookpost': post, 'textbook': book})

def sendEmail(request, pk):

    #Send email from buyer to poster
    post = TextbookPost.objects.get(pk=pk)
    subject = request.POST['subject']
    Message = request.POST['message']
    from_email = request.POST['from_email']
    to_email = request.POST['to_email']
    if Message == '':
         Message = f"Hi! I am interested in buying your textbook {post.textbook.title} for the set price of {post.price} through {post.payment}. Please email me back when you can meet at your convienence."
    send_mail(
        subject,
        Message,
        from_email,
        [to_email],
        fail_silently=False,
    )

    #Send confirmation email to buyer
    subject_conf = 'Email confirmation'
    message_conf = f"The following message was sent to {to_email}:\n\n" + Message
    send_mail(
        subject_conf,
        message_conf,
        from_email,
        [from_email],
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


def class_search_view(request):
    return render(request, 'txtbook/search_by_class.html')

def search_by_class(request):
    template = 'txtbook/search_by_class.html'
    dept = request.GET.get('class')
    nbr = str(request.GET.get('nbr'))
    results = []
    if( dept == False and nbr == False):
        return render(request, 'txtbook/search_by_class.html')
    elif( dept.isalpha() != True and dept == False or dept== False and dept.length > 4):
        return render(request, 'txtbook/search_by_class.html',{'error_message': "Invalid Class department" })
    elif( nbr.isnumeric() != True and nbr == False or nbr == False and nbr.length > 4):
        return render(request, 'txtbook/search_by_class.html',{'error_message': "Invalid Course Number" })
    print(dept is not False)
    if(nbr == "" and dept != ""):
        results = Textbook.objects.filter(Q(dept=dept.upper().strip())).order_by('classnum')
    elif( dept == "" and nbr != ""):
        results = Textbook.objects.filter(Q(classnum__icontains=nbr.strip())).order_by('dept','classnum')
    elif( dept != "" and nbr != ""):
        results = Textbook.objects.filter(Q(dept=dept.upper().strip())).filter(Q(classnum__icontains=nbr.strip())).order_by('dept','classnum')
    else:
        return render(request,'txtbook/search_by_class.html',{})
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
    return render(request,'txtbook/search_by_class.html', {'books': books, 'page_range':page_range, 'dept':dept, 'num':nbr})


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
    if query == '' or query == None:
        results = Textbook.objects.all().order_by('dept','classnum')
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
        new_maxdiff = str(request.POST['maxDiff'])
        new_payment = request.POST['payment']
        new_condition = request.POST['inlineRadioOptions']
        new_additional_info = request.POST['additionalInfo']
        new_format = request.POST['format']
        new_image = request.FILES.get('image', False)
        new_email = request.POST['email']
        profile_id = request.POST['profile']

        if (new_price != ''):
            new_price = float(new_price)

        if (new_price == ''):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Your posting MUST have a price."})

        if (float(new_price) > 10000):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Please input a reasonable price."})

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/addExistingTextbook.html', {'textbook': Textbook.objects.get(id=pk),
                                                                            'error_message': "Maximum price difference must be less than or equal to the price of the textbook."})
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if (new_email == ''):
            return render(request, 'txtbook/addExistingTextbook.html',
                          {'textbook': Textbook.objects.get(id=pk), 'error_message': "You must be logged in to post a textbook."})

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/addExistingTextbook.html',
            #               {'textbook': Textbook.objects.get(id=pk),
            #                'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."})

    except (KeyError, TextbookPost.DoesNotExist):
        return render(request, 'txtbook/addExistingTextbook.html', {
            # 'error_message': "One or more of the fields is empty."
        })
    else:

        if (new_price != ''):
            new_price = float(new_price)

        if (new_price == ''):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Your posting MUST have a price."})

        if (float(new_price) > 10000):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Please input a reasonable price."})

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/addExistingTextbook.html', {'textbook': Textbook.objects.get(id=pk),
                                                                            'error_message': "Maximum price difference must be less than or equal to the price of the textbook."})
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if (new_email == ''):
            return render(request, 'txtbook/addExistingTextbook.html',
                          {'textbook': Textbook.objects.get(id=pk), 'error_message': "You must be logged in to post a textbook."})

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/addExistingTextbook.html',
            #               {'textbook': Textbook.objects.get(id=pk),
            #                'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."})

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
            sold=False,
        )
        tp.save()
        return HttpResponseRedirect(tp.get_absolute_url())
    # return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk)})

# Main page to add a textbook.
def addTextbook(request):
        try:
            user = request.user

            if user.is_anonymous == False:
                try:
                    if user.profile.id == '':
                        return render(request, 'txtbook/create_profile.html')
                except:
                    return render(request, 'txtbook/create_profile.html')

            new_title = request.POST['title']
            new_author = request.POST['author']
            new_dept = request.POST['dept']
            new_classnum = str(request.POST['classnum'])
            new_isbn = request.POST['isbn']
            new_sect = str(request.POST['sect'])
            new_price = request.POST['price']
            new_negotiable = request.POST['negotiable']
            new_exchangable = request.POST['exchangable']
            new_maxdiff = str(request.POST['maxDiff'])
            new_payment = request.POST['payment']
            new_condition = request.POST['inlineRadioOptions']
            new_additional_info = request.POST['additionalInfo']
            new_format = request.POST['format']
            new_image = request.FILES.get('image', False)
            new_email = request.POST['email']
            profile_id = request.POST['profile']

            if (new_price != ''):
                new_price = float(new_price)

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
                })

            if (new_email == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "You must be logged in to post a textbook"
                })
            if (new_price > 10000):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Please enter a reasonable price."
                })

            if (new_maxdiff != ''):
                if (float(new_maxdiff) > new_price):
                    return render(request, 'txtbook/addTextbook.html', {
                        'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                    })
                new_maxdiff = str(float(new_maxdiff))
                if new_maxdiff[-2] == '.':
                    new_maxdiff += '0'
                if new_maxdiff[0] == '.':
                    new_maxdiff = '0' + new_maxdiff

            if new_exchangable == 'No':
                new_maxdiff = ''
                # return render(request, 'txtbook/addTextbook.html', {
                #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
                # })


        except (KeyError, TextbookPost.DoesNotExist):
            return render(request, 'txtbook/addTextbook.html', {
                # 'error_message': "One or more of the fields is empty."
            })

        else:

            if (new_price != ''):
                new_price = float(new_price)

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
                })

            if (new_email == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "You must be logged in to post a textbook"
                })

            if (new_price > 10000):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Please enter a reasonable price."
                })

            if (new_maxdiff != ''):
                if (float(new_maxdiff) > new_price):
                    return render(request, 'txtbook/addTextbook.html', {
                        'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                    })
                new_maxdiff = str(float(new_maxdiff))
                if new_maxdiff[-2] == '.':
                    new_maxdiff += '0'
                if new_maxdiff[0] == '.':
                    new_maxdiff = '0' + new_maxdiff

            if new_exchangable == 'No':
                new_maxdiff = ''
                # return render(request, 'txtbook/addTextbook.html', {
                #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
                # })

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
                sold=False,
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


register = template.Library()


@register.simple_tag(takes_context=True)
def filtered_posts_search(request):
    template = "txtbook/allPosts.html"
    model = TextbookPost
    context = TextbookPost

    filter_data = {}
    results = []

    query = request.GET.get('q')

    sort_date = request.GET.get('inlineRadioOptions')
    max_price = request.GET.get('max_price')

    dept = request.GET.get('dept')
    class_num = str(request.GET.get('class_num'))

    # query = request.POST['q']
    # sort_date = request.POST['inlineRadioOptions']
    # max_price = request.POST['max_price']
    # dept = request.POST['dept']
    # class_num = request.POST['class_num']

    # num_results = request.POST.get('num_results', False)

    # if num_results != '':
    #     num_results = int(num_results)
    # else:
    #     num_results = 20

    # if dept == None:
    #     dept = ''
    #
    # if class_num == None:
    #     class_num = ''
    #
    # if sort_date == None:
    #     sort_date = 'newest'
    #
    # if query == None:
    #     query == ''
    #
    # if max_price == None:
    #     max_price == ''


    # filter_data = {
    #     'search_term': query,
    #     'sort_date': sort_date,
    #     'max_price': max_price,
    #     'dept': dept,
    #     'class_num': class_num,
    # }

    if sort_date == 'newest':
        results = TextbookPost.objects.filter(
            Q(textbook__title__icontains=query) | Q(textbook__author__icontains=query) | Q(
                email__icontains=query), date_published__lte=timezone.now(),
                sold=False).order_by('-date_published')
    else:
        results = TextbookPost.objects.filter(
            Q(textbook__title__icontains=query) | Q(textbook__author__icontains=query) | Q(
                email__icontains=query), date_published__lte=timezone.now(),
            sold=False).order_by('date_published')

    if max_price != '' and max_price != None:
        results = results.filter(
            Q(textbook__title__icontains=query) | Q(textbook__author__icontains=query) | Q(
                email__icontains=query), sold=False,
                price__lte=float(max_price))
    if dept != '':
        results = results.filter(textbook__dept=dept)
        if class_num != '':
            results = results.filter(textbook__classnum=class_num)

    posts = results

    # paginator = Paginator(results, 2)
    # page_request_var = 'page'
    # page = request.GET.get(page_request_var)
    # try:
    #     posts = paginator.page(page)
    # except PageNotAnInteger:
    #     posts = paginator.page(1)
    # except EmptyPage:
    #     posts = paginator.page(paginator.num_pages)
    # index = posts.number - 1
    # max_index = len(paginator.page_range)
    # start_index = index - 5 if index >= 5 else 0
    # end_index = index + 5 if index <= max_index - 5 else max_index
    # page_range = paginator.page_range[start_index:end_index]

    # filter_data.update({
    #     'dept': dept,
    #     'class_num': class_num,
    #     'sort_date': sort_date,
    #     'search_term': query,
    #     'max_price': max_price,
    #     'latest_post_list': posts,
    # })

    return render(request, 'txtbook/filtered_posts_search.html',
                      {'latest_post_list': posts, 'max_price': max_price, 'sort_date': sort_date, 'search_term': query,
                       'dept': dept, 'class_num': class_num})



# Code to get the ForeignKey set for an object:
# https://stackoverflow.com/questions/51950416/reversemanytoonedescriptor-object-has-no-attribute-all/51950693
class profile_page(generic.DetailView):
    template_name = 'txtbook/profile_page.html'
    model = Profile
    # textbook_posts = User.textbookpost_set.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['textbook_posts'] = instance.textbookpost_set.filter(sold=False)
        context['textbook_posts_sold'] = instance.textbookpost_set.filter(sold=True)
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


def edit_post_database_text(request, pk):
    try:
        tp = TextbookPost.objects.get(id=pk)

        new_price = request.POST['price']
        new_negotiable = request.POST['negotiable']
        new_exchangable = request.POST['exchangable']
        new_maxdiff = str(request.POST['maxDiff'])
        new_payment = request.POST['payment']
        new_condition = request.POST['inlineRadioOptions']
        new_additional_info = request.POST['additionalInfo']
        new_format = request.POST['format']
        delete_image = request.POST['delete_image']

        if (new_price != ''):
            new_price = float(new_price)

        if tp.image == 'False':
            new_image = request.FILES.get('image', False)
        else:
            if delete_image == 'delete_image':
                new_image = False
            else:
                if request.FILES.get('image', False) == False:
                    new_image = tp.image
                else:
                    new_image = request.FILES.get('image', False)



        if (new_price == ''):
            return render(request, 'txtbook/edit_post_database_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

        if (float(new_price) > 10000):
            return render(request, 'txtbook/edit_post_database_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Please input a reasonable price"
            })

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/edit_post_database_text.html', {
                    'textbookpost': TextbookPost.objects.get(id=pk),
                    'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                })
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/edit_post_database_text.html', {
            #     'textbookpost': TextbookPost.objects.get(id=pk),
            #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
            # })

    except (KeyError, Profile.DoesNotExist):
        return render(request, 'txtbook/edit_post_database_text.html', {
            'textbookpost': TextbookPost.objects.get(id=pk),
        })

    else:

        if (new_price == ''):
            return render(request, 'txtbook/edit_post_database_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

        if (float(new_price) > 10000):
            return render(request, 'txtbook/edit_post_database_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Please input a reasonable price"
            })

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/edit_post_database_text.html', {
                    'textbookpost': TextbookPost.objects.get(id=pk),
                    'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                })
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/edit_post_database_text.html', {
            #     'textbookpost': TextbookPost.objects.get(id=pk),
            #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
            # })

        tp.price = new_price
        tp.negotiable = new_negotiable
        tp.exchangable = new_exchangable
        tp.max_diff = new_maxdiff
        tp.payment = new_payment
        tp.condition = new_condition
        tp.additional_info = new_additional_info
        tp.format = new_format
        tp.image = new_image
        tp.date_published = timezone.now()

        tp.save()

        return HttpResponseRedirect(tp.get_absolute_url())


def edit_post_original_text(request, pk):
    try:

        tp = TextbookPost.objects.get(id=pk)

        new_title = request.POST['title']
        new_author = request.POST['author']
        new_dept = request.POST['dept']
        new_classnum = str(request.POST['classnum'])
        new_isbn = request.POST['isbn']
        new_sect = str(request.POST['sect'])

        new_price = request.POST['price']
        new_negotiable = request.POST['negotiable']
        new_exchangable = request.POST['exchangable']
        new_maxdiff = str(request.POST['maxDiff'])
        new_payment = request.POST['payment']
        new_condition = request.POST['inlineRadioOptions']
        new_additional_info = request.POST['additionalInfo']
        new_format = request.POST['format']
        delete_image = request.POST['delete_image']

        if (new_price != ''):
            new_price = float(new_price)

        if tp.image == 'False':
            new_image = request.FILES.get('image', False)
        else:
            if delete_image == 'delete_image':
                new_image = False
            else:
                if request.FILES.get('image', False) == False:
                    new_image = tp.image
                else:
                    new_image = request.FILES.get('image', False)

        if new_title == '' or new_price == '':
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Your textbook MUST have a title and price."
            })

        if (new_price == ''):
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

        if (float(new_price) > 10000):
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Please input a reasonable price."
            })

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/edit_post_original_text.html', {
                    'textbookpost': TextbookPost.objects.get(id=pk),
                    'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                })
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/edit_post_original_text.html', {
            #     'textbookpost': TextbookPost.objects.get(id=pk),
            #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
            # })

    except (KeyError, Profile.DoesNotExist):
        return render(request, 'txtbook/edit_post_original_text.html', {
            'textbookpost': TextbookPost.objects.get(id=pk),
        })

    else:

        if new_title == '' or new_price == '':
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Your textbook MUST have a title and price."
            })

        if (new_price == ''):
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "You MUST fill out a price."
            })

        if (float(new_price) > 10000):
            return render(request, 'txtbook/edit_post_original_text.html', {
                'textbookpost': TextbookPost.objects.get(id=pk),
                'error_message': "Please input a reasonable price."
            })

        if (new_maxdiff != ''):
            if (float(new_maxdiff) > new_price):
                return render(request, 'txtbook/edit_post_original_text.html', {
                    'textbookpost': TextbookPost.objects.get(id=pk),
                    'error_message': "Maximum price difference must be less than or equal to the price of the textbook."
                })
            new_maxdiff = str(float(new_maxdiff))
            if new_maxdiff[-2] == '.':
                new_maxdiff += '0'
            if new_maxdiff[0] == '.':
                new_maxdiff = '0' + new_maxdiff

        if new_exchangable == 'No':
            new_maxdiff = ''
            # return render(request, 'txtbook/edit_post_original_text.html', {
            #     'textbookpost': TextbookPost.objects.get(id=pk),
            #     'error_message': "There cannot be a maximum price difference if the textbook is NOT exchangable."
            # })

        tp.textbook.title = new_title
        tp.textbook.author = new_author
        tp.textbook.dept = new_dept
        tp.textbook.classnum = new_classnum
        tp.textbook.isbn = new_isbn
        tp.textbook.sect = new_sect

        tp.textbook.save()

        tp.price = new_price
        tp.negotiable = new_negotiable
        tp.exchangable = new_exchangable
        tp.max_diff = new_maxdiff
        tp.payment = new_payment
        tp.condition = new_condition
        tp.additional_info = new_additional_info
        tp.format = new_format
        tp.image = new_image
        tp.date_published = timezone.now()

        tp.save()

        return HttpResponseRedirect(tp.get_absolute_url())


def delete_post(request, post_pk, profile_pk):
    tp = TextbookPost.objects.get(id=post_pk)
    tp.delete()

    profile = Profile.objects.get(id=profile_pk)

    return HttpResponseRedirect(profile.get_absolute_url())


def mark_post_sold(request, pk):
    tp = TextbookPost.objects.get(id=pk)
    tp.sold = True
    tp.save()

    return HttpResponseRedirect(tp.get_absolute_url())


def repost(request, pk):
    tp = TextbookPost.objects.get(id=pk)
    tp.sold = False
    tp.save()

    return HttpResponseRedirect(tp.get_absolute_url())


def search_options(request):
    return render(request, 'txtbook/search_options.html')