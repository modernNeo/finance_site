from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import ItemRefund
from finance_site.models.ItemModels import Item
from finance_site.models.TransactionModels import Transaction


class NewItemRefundMapping(View):

    def get(self, request):
        charges = Item.objects.all().filter(transaction__payment_method__in=["MasterCard", "Debit Card"], price__lt=0)
        refunds = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_item_refund_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        item_refund_mapping = ItemRefund()
        item_refund_mapping.refund_transaction = Transaction.objects.get(id=post_dict['refund_transaction'])
        item_refund_mapping.original_item = Item.objects.get(id=post_dict['original_item'])
        item_refund_mapping.save()
        return HttpResponseRedirect(item_refund_mapping.get_update_link)
