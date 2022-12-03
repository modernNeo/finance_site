from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import TransactionRefund
from finance_site.models.TransactionModels import Transaction


class UpdateTransactionRefundMapping(View):

    def get(self, request, mapping_id):
        transaction_refund_mapping = TransactionRefund.objects.get(id=mapping_id)
        charges = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0)
        return render(
            request, 'create_or_update_transaction_refund_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "transaction_refund_mapping": transaction_refund_mapping,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        transaction_refund_mapping = TransactionRefund.objects.get(id=mapping_id)
        transaction_refund_mapping.refund_transaction = Transaction.objects.get(id=post_dict['refund_transaction'])
        transaction_refund_mapping.original_transaction = Transaction.objects.get(id=post_dict['original_transaction'])
        transaction_refund_mapping.save()
        return HttpResponseRedirect(f"/mapping/refund/transaction/update/{transaction_refund_mapping.id}")
