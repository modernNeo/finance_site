from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance_site.models.TransactionModels import PendingTransaction, TransactionBase, Transaction, TransactionCategory


class UpdatePendingTransaction(View):
    def get(self, request, pending_transaction_id):
        pending_transaction = PendingTransaction.objects.get(id=pending_transaction_id)
        return render(
            request, 'create_or_update_pending_transaction.html',
            context={
                "pending_transaction": pending_transaction,
                "payment_method_choices": [payment_choice[0] for payment_choice in
                                           TransactionBase.payment_method_choices],
                "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                            TransactionBase.purchase_target_choices],
                "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                         Transaction.who_will_pay_choices],
                "categories": TransactionCategory.objects.all()
            }
        )

    def post(self, request, pending_transaction_id):
        if request.POST['action'] == "create_or_update_pending_transaction":
            pending_transaction = PendingTransaction.objects.get(id=pending_transaction_id)
            pending_transaction.month = request.POST['month']
            pending_transaction.date = request.POST['date']
            pending_transaction.payment_method = request.POST['payment_method']
            pending_transaction.purchase_target = request.POST['purchase_target']
            pending_transaction.who_will_pay = request.POST['who_will_pay']
            pending_transaction.price = request.POST['price']
            pending_transaction.store = request.POST['store']
            pending_transaction.note = request.POST['note']
            pending_transaction.category = TransactionCategory.objects.get(id=request.POST['category'])
            receipt = request.FILES.get('receipt', None)
            file_name = None
            if receipt is not None:
                fs = FileSystemStorage()
                file_name = fs.save(receipt.name, receipt)
            pending_transaction.receipt = file_name
            pending_transaction.save()
            return HttpResponseRedirect(pending_transaction.get_update_link)
        else:
            PendingTransaction.objects.get(id=pending_transaction_id).delete()
            return HttpResponseRedirect("/pending_transactions")
