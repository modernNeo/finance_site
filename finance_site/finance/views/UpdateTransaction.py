from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import Transaction, TransactionBase, TransactionCategory


class UpdateTransaction(View):
    def get(self, request, transaction_id):
        transaction = Transaction.objects.get(id=transaction_id)
        transactions_refunding_this_transaction = transaction.get_transactions_refunding_this_transaction()
        transactions_this_transaction_refunds = transaction.get_transactions_this_transaction_is_refunding()
        corresponding_internal_transfers = transaction.get_any_internal_transfers_mapped_to_this_etransfer()
        corresponding_e_transfers = transaction.get_any_etransfers_mapped_to_this_internal_transfer()
        transactions_reimbursing_this_transaction = transaction.get_transactions_reimbursing_this_transaction()
        transactions_this_transaction_reimburses = transaction.get_transactions_this_transaction_is_reimbursing()

        labels = transaction.transactionlabelintersection_set.all()
        items = transaction.item_set.all()
        reimbursed_items = [
            transactions_obj.item_set.all()
            for transactions_obj in transactions_reimbursing_this_transaction
        ]
        return render(request, 'update_transaction.html', {
            "transaction": transaction,
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     Transaction.who_will_pay_choices],
            "categories": TransactionCategory.objects.all(),
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
        transaction = Transaction.objects.get(id=transaction_id)
        receipt = request.FILES.get("receipt", None)
        file_name = None
        if receipt is not None:
            fs = FileSystemStorage()
            file_name = fs.save(receipt.name, receipt)
        transaction.month = request.POST['month']
        transaction.date = request.POST['date']
        transaction.payment_method = request.POST['payment_method']
        transaction.purchase_target = request.POST['purchase_target']
        transaction.who_will_pay = request.POST['who_will_pay']
        transaction.store = request.POST['store']
        transaction.note = request.POST['note']
        if file_name is not None:
            if transaction.receipt.name is not None and (file_name != transaction.receipt):
                fs.delete(transaction.receipt.name)
            transaction.receipt = file_name
        transaction.categories = Transaction.objects.get(id=request.POST['categories'])
        transaction.save()
        return HttpResponseRedirect(transaction.get_update_link)
