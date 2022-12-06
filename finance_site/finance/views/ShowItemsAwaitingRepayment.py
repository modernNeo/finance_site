from django.shortcuts import render
from django.views.generic.base import View

from finance.models.TransactionModels import FinalizedTransaction


class ShowItemsAwaitingRepayment(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(price__lt=0).order_by('-date')
        items_waiting_repayment = []
        transactions_waiting_repayment = []
        for transaction in transactions:
            if transaction.category is not None:
                if transaction.category.category == "Partial":
                    for item in transaction.finalizeditem_set.all():
                        if item.category.category == "Not My Expense":
                            refund_exists = False
                            reimbursement_exists = False
                            paid_back_exists = False
                            refunds = item.refunds_mapping_set.all()
                            for refund in refunds:
                                if refund.refund_transaction is not None:
                                    refund_exists = refund_exists or True
                            if not refund_exists:
                                reimbursements = item.reimbursements_mapping_set.all()
                                for reimbursement in reimbursements:
                                    if reimbursement.reimbursement_transaction is not None:
                                        reimbursement_exists = reimbursement_exists or True
                            if not refund_exists and not reimbursement_exists:
                                paybacks = item.paybacks_mapping_set.all()
                                for payback in paybacks:
                                    if payback.payback_transaction is not None:
                                        paid_back_exists = paid_back_exists or True
                            if not refund_exists and not reimbursement_exists and not paid_back_exists:
                                items_waiting_repayment.append(item)
                elif transaction.category.category == "Not My Expense":
                    refund_exists = False
                    reimbursement_exists = False
                    paid_back_exists = False
                    refunds = transaction.refunds_mapping_set.all()
                    for refund in refunds:
                        if refund.refund_transaction is not None:
                            refund_exists = refund_exists or True
                    if not refund_exists:
                        reimbursements = transaction.reimbursements_mapping_set.all()
                        for reimbursement in reimbursements:
                            if reimbursement.reimbursement_transaction is not None:
                                reimbursement_exists = reimbursement_exists or True
                    if not refund_exists and not reimbursement_exists:
                        paybacks = transaction.paybacks_mapping_set.all()
                        for payback in paybacks:
                            if payback.payback_transaction is not None:
                                paid_back_exists = paid_back_exists or True
                    if not refund_exists and not reimbursement_exists and not paid_back_exists:
                        transactions_waiting_repayment.append(transaction)
        return render(
            request, 'awaiting_reimbursement.html', context=
            {
                "items_waiting_repayment": items_waiting_repayment,
                "transactions_waiting_repayment": transactions_waiting_repayment,
                "current_page": "not_reimbursed"
            }
        )
