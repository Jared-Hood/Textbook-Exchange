# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template import loader
import csv, io
from .models import Textbook, TextbookPost


def index(request):
    return render(request, 'txtbook/bootstrap-landing.html')

# def addTextbook(request):
#     return render(request, 'txtbook/addtextbook.html')

# def allPosts(request):
#     return render(request, 'txtbook/allposts.html')

class allPostsView(generic.ListView):
    template_name = 'txtbook/allPosts.html'
    context_object_name = 'latest_post_list'

    def get_queryset(self):
        """
        Return all posts, ordered by most recent publish date.
        """
        return TextbookPost.objects.filter(
            datePublished__lte=timezone.now()
        ).order_by('-datePublished')

class PostView(generic.DetailView):
    model = TextbookPost
    template_name = 'txtbook/post.html'
    context = TextbookPost
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return TextbookPost.objects.filter(datePublished__lte=timezone.now())

def addTextbook(request):
# <<<<<<< HEAD
    try:
        newTitle = request.POST['title']
        newAuthor = request.POST['author']
        newDept = request.POST['dept']
        newClassnum = request.POST['classnum']
        newIsbn = request.POST['isbn']
        newSect = request.POST['sect']
        newPrice = request.POST['price']
        newNegotiable = request.POST['negotiable']
        newExchangable = request.POST['exchangable']
        newMaxDiff = request.POST['maxDiff']
        newPayment = request.POST['payment']
        newCondition = request.POST['inlineRadioOptions']
        newAdditionalInfo = request.POST['additionalInfo']
        newFormat = request.POST['format']

        if (newTitle == '' or newPrice == ''):
            return render(request, 'txtbook/addTextbook.html', {
                'error_message': "Your textbook must have a TITLE and PRICE."
            })

    except (KeyError, TextbookPost.DoesNotExist):
        return render(request, 'txtbook/addTextbook.html', {
            # 'error_message': "One or more of the fields is empty."
        })

    else:
        tp = TextbookPost(
            title=newTitle,
            author=newAuthor,
            dept=newDept,
            classnum=newClassnum,
            isbn=newIsbn,
            sect=newSect,
            price=newPrice,
            negotiable=newNegotiable,
            exchangable=newExchangable,
            maxDiff=newMaxDiff,
            payment=newPayment,
            condition=newCondition,
            additionalInfo=newAdditionalInfo,
            format=newFormat,
            datePublished=timezone.now()
        )
        tp.save()
        return HttpResponseRedirect(reverse('txtbook:addTextbook'))
# =======
    return render(request, 'txtbook/addTextbook.html')
# >>>>>>> 0b2597a8a7905ec2e8f13a8e580f82950ccaf5eb

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
            dept=column[0],classnum=column[1],sect=column[2],title=column[4],author=column[5],isbn=column[6], newPriceBookstore=column[7],usedPriceBookstore=column[8],amazonLink=column[9]
        )
    context = {}
    return render(request,template,context)
