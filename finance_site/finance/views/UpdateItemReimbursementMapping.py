from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.GroupingModels import ItemReimbursement
from finance.models.ItemModels import FinalizedItem
from finance.models.TransactionModels import FinalizedTransaction


class UpdateItemReimbursementMapping(View):

    def get(self, request, mapping_id):
        item_reimbursement_mapping = ItemReimbursement.objects.get(id=mapping_id)
        charges = FinalizedItem.objects.all().filter(transaction__payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_item_reimbursement_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "item_reimbursement_mapping": item_reimbursement_mapping,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        item_reimbursement_mapping = ItemReimbursement.objects.get(id=mapping_id)
        item_reimbursement_mapping.reimbursement_transaction = FinalizedTransaction.objects.get(
            id=post_dict['reimbursement_transaction'])
        item_reimbursement_mapping.original_item = FinalizedItem.objects.get(id=post_dict['original_item'])
        item_reimbursement_mapping.save()
        return HttpResponseRedirect(item_reimbursement_mapping.get_update_link)
