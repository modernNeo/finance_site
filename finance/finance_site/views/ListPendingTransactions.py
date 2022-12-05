from django.shortcuts import render
from django.views import View

from finance_site.models.TransactionModels import PendingTransaction


class ListPendingTransactions(View):
    def get(self, request):
        transaction_and_items = []
        for pending_transaction in PendingTransaction.objects.all().order_by('-date'):
            transaction_and_items.append(pending_transaction)
            for pending_item in pending_transaction.pendingitem_set.all():
                transaction_and_items.append(pending_item)
        return render(request, 'list_of_pending_transactions.html', context={
            "pending_transactions": transaction_and_items,
            "current_page" : "pending"
        })
