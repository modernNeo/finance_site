from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import ItemReimbursement
from finance_site.models.ItemModels import Item
from finance_site.models.TransactionModels import Transaction


class UpdateItemReimbursementMapping(View):

    def get(self, request, mapping_id):
        item_reimbursement_mapping = ItemReimbursement.objects.get(id=mapping_id)
        charges = Item.objects.all().filter(transaction__payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0)
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
        item_reimbursement_mapping.reimbursement_transaction = Transaction.objects.get(
            id=post_dict['reimbursement_transaction'])
        item_reimbursement_mapping.original_item = Item.objects.get(id=post_dict['original_item'])
        item_reimbursement_mapping.save()
        return HttpResponseRedirect(f"/mapping/reimbursement/item/update/{item_reimbursement_mapping.id}")
