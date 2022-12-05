import datetime

from django.shortcuts import render
from django.views.generic.base import View

from finance.models.TransactionModels import Transaction


class ShowUncategorizedDebitCardTransactions(View):
    def get(self, request):
        transactions = Transaction.objects.all().filter(
            payment_method="Debit Card", category__isnull=True
        ).order_by('-date')
        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "transactions": transactions,
                "current_page": "uncategorized_debit_card",
                "transaction_type" : "Debit Card"
            }
        )

