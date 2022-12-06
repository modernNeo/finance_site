import datetime

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
            request, 'index.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "current_page": "all_debit_card",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m")
            }
        )