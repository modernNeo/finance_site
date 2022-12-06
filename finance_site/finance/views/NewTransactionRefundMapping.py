from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.GroupingModels import TransactionRefund
from finance.models.TransactionModels import FinalizedTransaction


class NewTransactionRefundMapping(View):

    def get(self, request):
        charges = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0).order_by('-date')
        refunds = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_transaction_refund_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        transaction_refund_mapping = TransactionRefund()
        transaction_refund_mapping.refund_transaction = FinalizedTransaction.objects.get(id=post_dict['refund_transaction'])
        transaction_refund_mapping.original_transaction = FinalizedTransaction.objects.get(id=post_dict['original_transaction'])
        transaction_refund_mapping.save()
        return HttpResponseRedirect(transaction_refund_mapping.get_update_link)
