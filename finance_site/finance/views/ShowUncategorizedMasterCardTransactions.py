import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from querystring_parser import parser

from finance.models.TransactionModels import Transaction, TransactionCategory


class ShowUncategorizedMasterCardTransactions(View):
    def get(self, request):
        transactions = Transaction.objects.all().filter(
            payment_method="MasterCard", category__isnull=True
        ).order_by('-date')
        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "transactions": transactions,
                "current_page": "uncategorized_master_card",
                "transaction_type" : "MasterCard"
            }
        )