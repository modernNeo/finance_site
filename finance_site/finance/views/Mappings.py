from django.shortcuts import render
from django.views import View

from finance.models.GroupingModels import TransactionRefund, ETransferToInternalTransferMapping, \
    TransactionReimbursement, ItemReimbursement, ItemPayBack, TransactionPayBack, ItemRefund


class Mappings(View):

    def get(self, request):
        return render(
            request, 'mappings.html', context=
            {
                "current_page": "mappings",
                "transaction_refund_mappings": TransactionRefund.objects.all(),
                "transaction_reimbursement_mappings": TransactionReimbursement.objects.all(),
                "transaction_paid_back_mappings": TransactionPayBack.objects.all(),
                "item_refund_mappings": ItemRefund.objects.all(),
                "item_reimbursement_mappings": ItemReimbursement.objects.all(),
                "item_paid_back_mappings": ItemPayBack.objects.all(),
                "e_transfer_to_internal_transfer_mappings": ETransferToInternalTransferMapping.objects.all(),
            }
        )
