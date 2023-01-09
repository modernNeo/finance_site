from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction, TransactionBase, TransactionCategory, Receipt


class UpdateTransaction(View):
    def get(self, request, transaction_id):
        finalized_transaction = FinalizedTransaction.objects.get(id=transaction_id)
        transactions_refunding_this_transaction = finalized_transaction.get_transactions_refunding_this_transaction()
        transactions_this_transaction_refunds = finalized_transaction.get_transactions_this_transaction_is_refunding()
        corresponding_internal_transfers = finalized_transaction.get_any_internal_transfers_mapped_to_this_etransfer()
        corresponding_e_transfers = finalized_transaction.get_any_etransfers_mapped_to_this_internal_transfer()
        transactions_reimbursing_this_transaction = finalized_transaction.get_transactions_reimbursing_this_transaction()
        transactions_this_transaction_reimburses = finalized_transaction.get_transactions_this_transaction_is_reimbursing()

        labels = finalized_transaction.transactionlabelintersection_set.all()
        items = finalized_transaction.finalizeditem_set.all()
        reimbursed_items = [
            transactions_obj.finalizeditem_set.all()
            for transactions_obj in transactions_reimbursing_this_transaction
        ]
        return render(request, 'update_transaction.html', {
            "transaction": finalized_transaction,
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     FinalizedTransaction.who_will_pay_choices],
            "categories": TransactionCategory.objects.all().order_by('order_number'),
            "transactions_refunding_this_transaction": transactions_refunding_this_transaction,
            "transactions_this_transaction_refunds": transactions_this_transaction_refunds,
            "corresponding_internal_transfers": corresponding_internal_transfers,
            "corresponding_e_transfers": corresponding_e_transfers,
            "transactions_reimbursing_this_transaction": transactions_reimbursing_this_transaction,
            "transactions_this_transaction_reimburses": transactions_this_transaction_reimburses,

            "labels": labels,
            "items": items,
            "reimbursed_items": reimbursed_items
        })

    def post(self, request, transaction_id):
        finalized_transaction = FinalizedTransaction.objects.get(id=transaction_id)
        finalized_transaction.month = request.POST['month']
        finalized_transaction.date = request.POST['date']
        finalized_transaction.payment_method = request.POST['payment_method']
        finalized_transaction.purchase_target = request.POST['purchase_target']
        finalized_transaction.who_will_pay = request.POST['who_will_pay']
        finalized_transaction.store = request.POST['store']
        if request.FILES.get("receipts", None) is not None:
            fs = FileSystemStorage()
            current_receipts = finalized_transaction.receipts.all()
            for current_receipt in current_receipts:
                fs.delete(current_receipt.receipt.name)
                current_receipt.delete()
            for receipt in (dict(request.FILES))['receipts']:
                new_receipt_name = fs.save(f"{finalized_transaction.date}-{receipt.name}", receipt)
                Receipt(receipt=new_receipt_name, transaction=finalized_transaction).save()
        finalized_transaction.note = request.POST['note']
        finalized_transaction.category = TransactionCategory.objects.get(id=request.POST['category'])
        finalized_transaction.save()
        return HttpResponseRedirect(finalized_transaction.get_update_link)
