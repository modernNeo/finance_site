import datetime

from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction


class ShowAllMasterCardTransactions(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(payment_method="MasterCard").order_by('-date')
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
            request, 'show_all_mastercard_transactions.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "current_page": "all_master_card",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m")
            }
        )