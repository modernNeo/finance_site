import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from querystring_parser import parser

from finance.models.TransactionModels import FinalizedTransaction, TransactionCategory


class ShowUncategorizedMasterCardTransactions(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(
            payment_method="MasterCard", category__isnull=True
        ).order_by('-date')
        uncategorized_transactions = []
        for transaction in transactions:
            uncategorized_transactions.append(transaction)
            for item in transaction.finalizeditem_set.all():
                uncategorized_transactions.append(item)
        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "uncategorized_transactions": uncategorized_transactions,
                "current_page": "uncategorized_master_card",
                "transaction_type": "MasterCard"
            }
        )
