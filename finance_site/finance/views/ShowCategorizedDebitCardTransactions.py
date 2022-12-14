import datetime

from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction


class ShowCategorizedDebitCardTransactions(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(
            payment_method="Debit Card", category__isnull=False
        ).order_by('-date')
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
            request, 'categorized_debit_card.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "current_page": "categorized_debit_card",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m")
            }
        )