from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.GroupingModels import TransactionPayBack, ItemPayBack
from finance.models.ItemModels import Item
from finance.models.TransactionModels import Transaction


class NewItemRepaidMapping(View):

    def get(self, request):
        charges = Item.objects.all().filter(transaction__payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_item_paid_back_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        item_repaid_mapping = ItemPayBack()
        item_repaid_mapping.payback_transaction = Transaction.objects.get(id=post_dict['payback_transaction'])
        item_repaid_mapping.original_item = Item.objects.get(id=post_dict['original_item'])
        item_repaid_mapping.save()
        return HttpResponseRedirect(item_repaid_mapping.get_update_link)
