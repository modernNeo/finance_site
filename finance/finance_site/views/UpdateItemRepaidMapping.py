from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import ItemPayBack
from finance_site.models.ItemModels import Item
from finance_site.models.TransactionModels import Transaction


class UpdateItemRepaidMapping(View):

    def get(self, request, mapping_id):
        item_repaid_mapping = ItemPayBack.objects.get(id=mapping_id)
        charges = Item.objects.all().filter(transaction__payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0)
        return render(
            request, 'create_or_update_item_paid_back_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "item_repaid_mapping": item_repaid_mapping,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        item_repaid_mapping = ItemPayBack.objects.get(id=mapping_id)
        item_repaid_mapping.payback_transaction = Transaction.objects.get(id=post_dict['payback_transaction'])
        item_repaid_mapping.original_item = Item.objects.get(id=post_dict['original_item'])
        item_repaid_mapping.save()
        return HttpResponseRedirect(f"/mapping/repaid/item/update/{item_repaid_mapping.id}")
