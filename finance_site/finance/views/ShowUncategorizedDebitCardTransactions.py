import datetime

from django.shortcuts import render
from django.views.generic.base import View

from finance.models.TransactionModels import Transaction


class ShowUncategorizedDebitCardTransactions(View):
    def get(self, request):
        transactions = Transaction.objects.all().filter(payment_method="Debit Card").order_by(
            '-date')
        uncategorized_transactions = []
        for transaction in transactions:
            if transaction.category is None and len(transaction.item_set.all()) == 0:
                uncategorized_transactions.append(transaction)

        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "transactions": uncategorized_transactions,
                "current_page": "uncategorized_debitcard"
            }
        )

