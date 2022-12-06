from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import PendingTransaction, TransactionCategory, TransactionBase, FinalizedTransaction
from finance.urls import update_pending_transaction


class NewPendingTransaction(View):
    def get(self, request):
        return render(
            request, 'create_or_update_pending_transaction.html',
            context={
                "current_page": "create_pending_transaction",
                "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
                "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in TransactionBase.purchase_target_choices],
                "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in FinalizedTransaction.who_will_pay_choices],
                "categories": TransactionCategory.objects.all().order_by('order_number')
            }
        )

    def post(self, request):
        receipt = request.FILES.get('receipt', None)
        file_name = None
        if receipt is not None:
            fs = FileSystemStorage()
            file_name = fs.save(receipt.name, receipt)
        pending_transaction = PendingTransaction(
            month=request.POST['month'],
            date=request.POST['date'],
            payment_method=request.POST['payment_method'],
            purchase_target=request.POST['purchase_target'],
            who_will_pay=request.POST['who_will_pay'],
            price=request.POST['price'],
            store=request.POST['store'],
            note=request.POST['note'],
            category=TransactionCategory.objects.get(id=request.POST['category']),
            receipt=file_name,
        )
        pending_transaction.save()
        return HttpResponseRedirect(pending_transaction.get_update_link)
