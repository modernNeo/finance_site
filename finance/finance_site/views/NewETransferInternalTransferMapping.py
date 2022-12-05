from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.GroupingModels import ETransferToInternalTransferMapping
from finance_site.models.TransactionModels import Transaction


class NewETransferInternalTransferMapping(View):

    def get(self, request):
        charges = Transaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0).order_by('-date')
        refunds = Transaction.objects.all().filter(payment_method__in=["Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_e_transfer_internal_transfer_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request):
        post_dict = parser.parse(request.POST.urlencode())
        e_transfer_to_internal_transfer_mapping = ETransferToInternalTransferMapping()
        e_transfer_to_internal_transfer_mapping.e_transfer = Transaction.objects.get(id=post_dict['etransfer'])
        e_transfer_to_internal_transfer_mapping.internal_transfer = Transaction.objects.get(id=post_dict['internal_transfer'])
        e_transfer_to_internal_transfer_mapping.save()
        return HttpResponseRedirect(e_transfer_to_internal_transfer_mapping.get_update_link)
