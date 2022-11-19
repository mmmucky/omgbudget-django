import csv
import datetime
import io
import re
import yaml

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Transaction, Classification, ClassificationRegex

from django.template import loader


class ClassificationView(generic.ListView):
    # template_name = 'transactions/home/index.html'
    # context_object_name = 'latest_question_list'
    model = Classification

    def get_queryset(self):
        """Return the classifications."""
        return Classification.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

class IndexView(generic.ListView):
    # template_name = 'transactions/home/index.html'
    # context_object_name = 'latest_question_list'
    model = Transaction

    def get_queryset(self):
        """Return the last transactions."""
        return Transaction.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


from .forms import UploadTransactionsForm
from .forms import UploadClassificationsForm

def handle_uploaded_classifications(f):
    print('processing classifications file')
    y = yaml.load(io.StringIO(f.read().decode("utf-8")), Loader=yaml.FullLoader)
    for bucket in y['expense_buckets']:
        print(bucket)
        c = Classification.objects.get_or_create(name=bucket['name'], classify_as=bucket['classify_as'])[0]
        print(c)
        for regex in bucket['regexes']:
            print(regex)
            print(c)
            print(dir(c))
            r = ClassificationRegex.objects.get_or_create(regex=regex, classification=c)
    do_update_classifications()

def do_update_classifications():
    # TODO: wipe all classifications to start, or detect/update existing state?
    transactions = Transaction.objects.all()
    classifications = Classification.objects.all()
    # Pre-compile all REs once and keep a list of (ORM object, compiled RE) tuples
    regexes = [(r, re.compile(r.regex)) for r in ClassificationRegex.objects.all()]

    print(f'Loaded {len(transactions)} transactions')
    print(f'Loaded {len(classifications)} classifications')
    print(f'Loaded {len(regexes)} regexes')
    # get a list of all regexes
    for t in transactions:
        for r, compiled_re in regexes:
            if re.match(compiled_re,t.other_party):
                print(f'{t} matched {r}')
                t.classifications.add(r.classification)

## Don't let anyone submit files.
def handle_uploaded_file(f):
    print(f)
    print(type(f))
    print(dir(f))
    csvreader = csv.reader(io.StringIO(f.read().decode("utf-8")), delimiter=",")
    # file = f.read().decode('utf-8')
    # reader = csv.DictReader(io.StringIO(file))
    for row in csvreader:
        # skip any rows that don't start with a valid date (header row)
        try:
            dt = datetime.datetime.strptime(row[0], "%d/%m/%Y").date()
        except:
            continue
#        t = Transaction(
#            trans_date=dt,
#            amount=row[1],
#            other_party=row[2],
#            description=row[3],
#            reference=row[4],
#            particulars=row[5],
#            analysis_code=row[6],
#        )
#        print(t)
        Transaction.objects.get_or_create(trans_date=dt,
            amount=row[1],
            other_party=row[2],
            description=row[3],
            reference=row[4],
            particulars=row[5],
            analysis_code=row[6],)

def upload_classifications(request):
    if request.method == "POST":
        form = UploadClassificationsForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_classifications(request.FILES["file"])
            return HttpResponseRedirect("/transactions/classifications")
        else:
            return HttpResponseRedirect("/transactions/upload_classifications/")
    else:
        # This is not a POST... return the file upload form.
        form = UploadClassificationsForm()
        context = {"segment": "index", "form": form}
        html_template = loader.get_template("upload_classifications.html")
        return HttpResponse(html_template.render(context, request))

def upload_file(request):
    if request.method == "POST":
        form = UploadTransactionsForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect("/transactions/")
        else:
            print(request.POST)
            print(request.POST["file"])
            return HttpResponseRedirect("/transactions/upload/")

    else:
        # This is not a POST... return the file upload form.
        form = UploadTransactionsForm()
        context = {"segment": "index", "form": form}
        html_template = loader.get_template("upload.html")
        return HttpResponse(html_template.render(context, request))


# def upload(request):
#     context = {"segment": "index"}
#     html_template = loader.get_template("upload.html")
#     return HttpResponse(html_template.render(context, request))


# def index(request):
#    return HttpResponse("Hello, world. You're at the transactions index.")


def home(request):
    context = {"segment": "index"}
    html_template = loader.get_template("home/index.html")
    return HttpResponse(html_template.render(context, request))
