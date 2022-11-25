import csv
from collections import defaultdict
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
    print("processing classifications file")
    y = yaml.load(io.StringIO(f.read().decode("utf-8")), Loader=yaml.FullLoader)
    for bucket in y["expense_buckets"]:
        print(bucket)
        c = Classification.objects.get_or_create(
            name=bucket["name"], classify_as=bucket["classify_as"]
        )[0]
        print(c)
        for regex in bucket["regexes"]:
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

    print(f"Loaded {len(transactions)} transactions")
    print(f"Loaded {len(classifications)} classifications")
    print(f"Loaded {len(regexes)} regexes")
    # get a list of all regexes
    for t in transactions:
        for r, compiled_re in regexes:
            if re.match(compiled_re, t.other_party):
                print(f"{t} matched {r}")
                t.classifications.add(r.classification)
                t.save()

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


# eventually report on expense buckets over time?
def expense_trends(request):
    pass

def report_list(request):
    ''' return an index of all valid report periods.  '''
    html_template = loader.get_template("report_list.html")
    context = {}
    months = set()
    for transaction in Transaction.objects.all():
        months.add(transaction.trans_date.strftime('%Y/%m'))
    context['sorted_months'] = sorted(months)
    return HttpResponse(html_template.render(context, request))

def report(request, year, month):
    first_of_month = datetime.date(year, month, 1)
    last_of_month = last_day_of_month(first_of_month)

    html_template = loader.get_template("report.html")
    context = {'year': year, 'month': month, 'list_transactions': False}

    # A set of expenses to *always* report on.
    # Always report these in the order provided, for easy month-to-month 
    # TODO: move to database
    # TODO: classify_as should be a property of a report, not a transaction
    # TODO: when there are multiple classifications, take the one that matches the longest substring of the transaction name?
    bucket_report_order = ['mortgage', 'house', 'groceries', 'food', 'bills', 'dog', 'unknown', 'other', 'entertainment', 'hair', 'shopping', 'rent', 'savings', 'term-deposit', 'transport', 'travel']
    # Track classifications observed over this report period
    classifications_seen = []
    # Build a dict that maps classification to lists of transactions during report period. (TODO: can the ORM do this via a GROUP BY style query?)
    transactions_by_classification = defaultdict(list)

    print('generating monthly summary...')
    context['total_in'] = 0
    context['total_out'] = 0

    transactions = Transaction.objects.filter(trans_date__range=[first_of_month.strftime("%Y-%m-%d"), last_of_month.strftime("%Y-%m-%d")])
    context['transactions'] = transactions
    expense_bucket_in = defaultdict(int)
    expense_bucket_out = defaultdict(int)

    # Sometimes we want to just print a list of all incoming money.
    credits = []

    for transaction in transactions:
        print(transaction)
        print(transaction.classifications.all())
        bucket = ''
        transaction_classifications = transaction.classifications.all()
        if transaction_classifications:
            bucket = transaction_classifications[0].classify_as or transaction_classifications[0].name
            print(f'{transaction_classifications[0]} {transaction_classifications[0].classify_as}')
        else:
            bucket = 'unknown'
        transactions_by_classification[bucket].append(transaction)

        if transaction.amount > 0:
            credits.append(transaction)
            context['total_in'] += transaction.amount
            expense_bucket_in[bucket] += transaction.amount
        else:
            context['total_out'] += transaction.amount
            expense_bucket_out[bucket] += transaction.amount
    context['expense_bucket_in'] = expense_bucket_in
    context['expense_bucket_out'] = expense_bucket_out
    context['expense_bucket_in'].default_factory = None
    context['expense_bucket_out'].default_factory = None
    context['transactions_by_classification'] = transactions_by_classification
    context['transactions_by_classification'].default_factory = None

    return HttpResponse(html_template.render(context, request))

#    1. Get all range of transactions to report on (typically monthly)
#    transactions = db.session.query(Transaction).filter(extract('year', Transaction.trans_date)==year).filter(extract('month', Transaction.trans_date)==month).all()

#    2. pre-fetch  classifications
#    #classifications = db.session.query(Classification).all()

#   # Create a set of expense buckets to track totals 
    expense_bucket_totals = defaultdict(int)

    # Sometimes we want to just print a list of all incoming money.
    credits = []
    classifications = set()
#    # For each transaction
#    for transaction in transactions:
         # Keep a total of money in and out.
#        if transaction.amount > 0:
#            credits.append(transaction)
#            total_in += transaction.amount
#        else:
#            total_out += transaction.amount
         # 1. Determine classification
         # 2. update totals
         # 3. track encountered classifications
#        if transaction.classification:
#            classify_as = transaction.classification.classify_as or transaction.classification.name
#            expense_bucket_totals[classify_as] += transaction.amount
#        else:
#            expense_bucket_totals['unknown'] += transaction.amount
#            classify_as = 'unknown'
#        classifications.add(classify_as)
#        print(f'{transaction.amount} - {transaction.other_party} - {classify_as}')
#
#    # 
#    for bucket in bucket_report_order:
#        print(f'{bucket} {expense_bucket_totals[bucket]:.0f}')
#
#    for bucket, total in expense_bucket_totals.items():
#        if not bucket in bucket_report_order:
#            print(f'{bucket} {total:.2f}')
#        #print(k,v)
#    # print all inbound money
#    print(f'All inbound money:')
#    for transaction in credits:
#        print(transaction)
#    # print total in
#    print(f'total in: {total_in}')
#    print(f'total out: {total_out}')



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
        Transaction.objects.get_or_create(
            trans_date=dt,
            amount=row[1],
            other_party=row[2],
            description=row[3],
            reference=row[4],
            particulars=row[5],
            analysis_code=row[6],
        )


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
