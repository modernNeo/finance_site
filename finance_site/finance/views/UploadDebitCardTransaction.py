import csv
import datetime

import pytz
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import Transaction


class UploadDebitCardTransaction(View):
    def get(self, request):
        return render(request, 'upload_csv.html', context={
            "transaction_type": "Debit Card",
            "current_page": "upload_master_card_csv"
        })

    def post(self, request):
        receipt = request.FILES.get("csv_upload", None)
        if receipt is not None:
            fs = FileSystemStorage()
            file_name = fs.save(receipt.name, receipt)
            print(receipt)
            print(file_name)
            with open(file_name, 'r') as debit_card_csv:
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
                        Transaction(
                            month=date,
                            date=date,
                            payment_method="MasterCard",
                            method_of_transaction=line[1],
                            name=line[2],
                            memo=line[3],
                            price=line[4]
                        ).save()
            fs.delete(file_name)
