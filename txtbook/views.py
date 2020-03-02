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
from .models import Textbook, TextbookPost
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.contrib.auth import logout

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
        Excludes any questions that aren't published yet.
        """
        return TextbookPost.objects.filter(date_published__lte=timezone.now())

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
        results = Textbook.objects.filter(Q(isbn__icontains=query_numeric) | Q(title__icontains=query) | Q(author__icontains=query)).distinct()
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

        if (new_price == ''):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Your posting MUST have a price."})

    except (KeyError, TextbookPost.DoesNotExist):
        return render(request, 'txtbook/addExistingTextbook.html', {
            # 'error_message': "One or more of the fields is empty."
        })
    else:
        tp = TextbookPost(
            textbook=Textbook.objects.get(id=pk),
            price=new_price,
            negotiable=new_negotiable,
            exchangable=new_exchangable,
            max_diff=new_maxdiff,
            payment=new_payment,
            condition=new_condition,
            additional_info=new_additional_info,
            format=new_format,
            date_published=timezone.now(),
            image=new_image
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

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
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

            book = Textbook.objects.create(title=new_title, author=new_author, dept=new_dept, classnum=new_classnum,
                                           sect=new_sect, isbn=new_isbn, user_created=True)
            book.save()
            tp = TextbookPost(
                textbook=book,
                price=new_price,
                negotiable=new_negotiable,
                exchangable=new_exchangable,
                max_diff=new_maxdiff,
                payment=new_payment,
                condition=new_condition,
                additional_info=new_additional_info,
                format=new_format,
                date_published=timezone.now(),
                image=new_image
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
    next(io_string)
    for column in csv.reader(io_string, delimiter='\t'):
        if(column[4] == ""):
            continue
        created = Textbook.objects.create(
            dept=column[0],classnum=column[1],sect=column[2],title=column[4],author=column[5],isbn=column[6], new_price_bookstore=column[7],used_price_bookstore=column[8],amazon_link=column[9]
        )
    context = {}
    return render(request,template,context)