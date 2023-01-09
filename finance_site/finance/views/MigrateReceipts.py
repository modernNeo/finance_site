import re
import shutil

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction, Receipt


class MigrateReceipts(View):

    def get(self, request):
        finalized_transactions = [finalized_transaction for finalized_transaction in FinalizedTransaction.objects.all() if finalized_transaction.receipt.name != ""]
        num_of_transactions = len(finalized_transactions)
        print(f"processing {num_of_transactions} transactions")
        for idx, finalized_transaction in enumerate(finalized_transactions):
            new_receipt_location = finalized_transaction.receipt
            if not re.match(r"\d{4}_\d{2}_\d{2}.*", finalized_transaction.receipt.name):
                new_receipt_name = f"{finalized_transaction.date.strftime('%Y-%m-%d')}-{finalized_transaction.receipt.name}"
                shutil.move(f"{settings.MEDIA_ROOT}/{finalized_transaction.receipt.name}", f"{settings.MEDIA_ROOT}/{new_receipt_name}")
                new_receipt_location = new_receipt_name
            Receipt(receipt=new_receipt_location, transaction=finalized_transaction).save()
            finalized_transaction.receipt = None
            finalized_transaction.save()
            print(f"processed {idx}/{num_of_transactions}")
        return HttpResponseRedirect("/")
