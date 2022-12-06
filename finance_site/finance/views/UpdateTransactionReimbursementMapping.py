from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.GroupingModels import TransactionReimbursement
from finance.models.TransactionModels import FinalizedTransaction


class UpdateTransactionReimbursementMapping(View):

    def get(self, request, mapping_id):
        transaction_reimbursement_mapping = TransactionReimbursement.objects.get(id=mapping_id)
        charges = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0).order_by('-date')
        refunds = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_transaction_reimbursement_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping",
                "transaction_reimbursement_mapping": transaction_reimbursement_mapping
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        transaction_reimbursement_mapping = TransactionReimbursement.objects.get(id=mapping_id)
        transaction_reimbursement_mapping.refund_transaction = FinalizedTransaction.objects.get(
            id=post_dict['reimbursement_transaction'])
        transaction_reimbursement_mapping.original_transaction = FinalizedTransaction.objects.get(
            id=post_dict['original_transaction'])
        transaction_reimbursement_mapping.save()
        return HttpResponseRedirect(transaction_reimbursement_mapping.get_update_link)
