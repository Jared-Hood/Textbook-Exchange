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


# Homepage
def index(request):
    return render(request, 'txtbook/bootstrap-landing.html')

# def addTextbook(request):
#     return render(request, 'txtbook/addtextbook.html')

# def allPosts(request):
#     return render(request, 'txtbook/allposts.html')


def text(request, pk):
    return render(request, 'txtbook/text.html', {'textbook': Textbook.objects.get(id=pk)})


def textView(request):
    all_text = Textbook.objects.all()
    context = {'books': all_text}
    return render(request,'txtbook/textlist.html',context)

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
    if query:
        if(query[0].isnumeric()):
            output = ""
            for char in query:
                if char == '-':
                    pass
                else:
                    output += char
            query = output
            results = Textbook.objects.filter(Q(isbn__icontains=query))
            context = {
                'books':results, 'search_term':query
                }
            return render(request, 'txtbook/search_results.html', context)
        else:
            results = Textbook.objects.filter(Q(title__icontains=query)|Q(author__icontains=query))
            context = {
                'books':results, 'search_term':query
                }
            return render(request, 'txtbook/search_results.html', context)

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

        if (new_price == ''):
            print("no new price")
            return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk), 'error_message': "Your posting MUST have price"})

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
            date_published=timezone.now()
        )
        tp.save()
        return HttpResponseRedirect(tp.get_absolute_url())
    # =======
    return render(request, 'txtbook/addExistingTextbook.html', {'textbook':Textbook.objects.get(id=pk)})
    # >>>>>>> 0b2597a8a7905ec2e8f13a8e580f82950ccaf5eb

# Main page to add a textbook.
def addTextbook(request):
# <<<<<<< HEAD
    if 'search' in request.GET:
        template = 'txtbook/search_results.html'
        if(request.GET['search'][0].isnumeric()):
            search_term = request.GET['search']
            temp = ''
            if '-' in search_term:
                for char in search_term:
                    if char == '-':
                        continue
                    else:
                        temp+=char
                search_term = temp
            output = []
            books = Textbook.objects.all()
            for book in books:
                if(search_term in book.isbn):
                    output.append(book)
            return render(request, template,  {'books': output, 'search_term': search_term})
        else:
            search_term = request.GET['search']
            output = []
            books = Textbook.objects.all()
            for book in books:
                if(search_term in book.title or search_term in book.author):
                    output.append(book)
            return render(request, template,  {'books': output, 'search_term': search_term})

    else:
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

            if (new_title == '' or new_price == ''):
                return render(request, 'txtbook/addTextbook.html', {
                    'error_message': "Your textbook must have a TITLE and PRICE."
                })

        except (KeyError, TextbookPost.DoesNotExist):
            return render(request, 'txtbook/addTextbook.html', {
                # 'error_message': "One or more of the fields is empty."
            })

        else:
            book = Textbook.objects.create(title=new_title, author=new_author, dept=new_dept, classnum = new_classnum, sect = new_sect,isbn = new_isbn, user_created = True)
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
                date_published=timezone.now()
            )
            tp.save()
            return HttpResponseRedirect(reverse('txtbook:addTextbook'))
    # =======
        return render(request, 'txtbook/addTextbook.html')
    # >>>>>>> 0b2597a8a7905ec2e8f13a8e580f82950ccaf5eb



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
