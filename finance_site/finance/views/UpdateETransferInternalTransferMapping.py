from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.GroupingModels import TransactionPayBack, ETransferToInternalTransferMapping
from finance.models.TransactionModels import FinalizedTransaction


class UpdateETransferInternalTransferMapping(View):

    def get(self, request, mapping_id):
        e_transfer_to_internal_transfer_mapping = ETransferToInternalTransferMapping.objects.get(id=mapping_id)
        charges = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__lt=0).order_by('-date')
        refunds = FinalizedTransaction.objects.all().filter(payment_method__in=["MasterCard", "Debit Card"], price__gt=0).order_by('-date')
        return render(
            request, 'create_or_update_e_transfer_internal_transfer_mapping.html', context=
            {
                "charges": charges,
                "refunds": refunds,
                "e_transfer_to_internal_transfer_mapping" : e_transfer_to_internal_transfer_mapping,
                "current_page": "refund_mapping"
            }
        )

    def post(self, request, mapping_id):
        post_dict = parser.parse(request.POST.urlencode())
        e_transfer_to_internal_transfer_mapping = ETransferToInternalTransferMapping.objects.get(id=mapping_id)
        e_transfer_to_internal_transfer_mapping.e_transfer = FinalizedTransaction.objects.get(id=post_dict['e_transfer'])
        e_transfer_to_internal_transfer_mapping.internal_transfer = FinalizedTransaction.objects.get(id=post_dict['internal_transfer'])
        e_transfer_to_internal_transfer_mapping.save()
        return HttpResponseRedirect(e_transfer_to_internal_transfer_mapping.get_update_link)
