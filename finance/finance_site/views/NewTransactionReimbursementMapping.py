from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import TransactionReimbursement
from finance_site.models.TransactionModels import Transaction


class NewTransactionReimbursementMapping(View):

    def get(self, request):
        charges = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0)
        return render(
            request, 'create_or_update_transaction_reimbursement_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        transaction_reimbursement_mapping = TransactionReimbursement()
        transaction_reimbursement_mapping.reimbursement_transaction = Transaction.objects.get(id=post_dict['reimbursement_transaction'])
        transaction_reimbursement_mapping.original_transaction = Transaction.objects.get(id=post_dict['original_transaction'])
        transaction_reimbursement_mapping.save()
        return HttpResponseRedirect(f"/mapping/reimbursement/transaction/update/{transaction_reimbursement_mapping.id}")
