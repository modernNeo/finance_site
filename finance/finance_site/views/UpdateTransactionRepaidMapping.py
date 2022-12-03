from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import TransactionPayBack
from finance_site.models.TransactionModels import Transaction


class UpdateTransactionRepaidMapping(View):

    def get(self, request, mapping_id):
        transaction_repaid_mapping = TransactionPayBack.objects.get(id=mapping_id)
        charges = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0)
        return render(
            request, 'create_or_update_transaction_paid_back_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "transaction_repaid_mapping": transaction_repaid_mapping,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        transaction_repaid_mapping = TransactionPayBack.objects.get(id=mapping_id)
        transaction_repaid_mapping.payback_transaction = Transaction.objects.get(id=post_dict['payback_transaction'])
        transaction_repaid_mapping.original_transaction = Transaction.objects.get(id=post_dict['original_transaction'])
        transaction_repaid_mapping.save()
        return HttpResponseRedirect(f"/mapping/repaid/transaction/update/{transaction_repaid_mapping.id}")
