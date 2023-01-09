import csv
import datetime

import pytz
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction


class ShowAllDebitCardTransactions(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(payment_method="Debit Card").order_by('-date')
        months = list(set([transaction.get_month for transaction in transactions]))
        months.sort()
        months = list(reversed(months))
        categorized_transactions = {}

        for transaction in transactions:
            if transaction.get_month not in categorized_transactions:
                categorized_transactions[transaction.get_month] = []
            categorized_transactions[transaction.get_month].append(transaction)
            for item in transaction.finalizeditem_set.all():
                categorized_transactions[transaction.get_month].append(item)
        return render(
            request, 'show_all_debit_card_transactions.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "current_page": "all_debit_card",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m"),
                "transaction_type": "Debit Card",
            }
        )

    def post(self, request):
        receipt = request.FILES.get("csv_upload", None)
        if receipt is not None:
            fs = FileSystemStorage()
            file_name = fs.save(receipt.name, receipt)
            print(receipt)
            print(file_name)
            file_name_and_path = f"{settings.MEDIA_ROOT}/{file_name}"
            with open(file_name_and_path, 'r') as debit_card_csv:
                csvFile = csv.reader(debit_card_csv)
                for line in csvFile:
                    date = None
                    try:
                        date = datetime.datetime.strptime(line[0], "%m/%d/%Y").astimezone(
                            pytz.timezone('America/Vancouver')
                        )
                    except ValueError:
                        pass
                    if date is not None:
                        FinalizedTransaction(
                            date=date,
                            payment_method="Debit Card",
                            method_of_transaction=line[1],
                            name=line[2],
                            memo=line[3],
                            price=line[4]
                        ).save()
            fs.delete(file_name)
        return HttpResponseRedirect("")