from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.ItemModels import FinalizedItem, PendingItem
from finance.models.TransactionModels import PendingTransaction, TransactionBase, TransactionCategory


class UpdatePendingItem(View):
    def get(self, request, pending_item_id):
        pending_item = PendingItem.objects.get(id=pending_item_id)
        pending_transactions = PendingTransaction.objects.filter(price__lt=0)
        return render(request, 'create_or_update_pending_item.html', context={
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     FinalizedItem.who_will_pay_choices],
            "categories": TransactionCategory.objects.all().order_by('order_number'),
            "pending_transactions": pending_transactions,
            "pending_item": pending_item
        })

    def post(self, request, pending_item_id):
        pending_item = PendingItem.objects.get(id=pending_item_id)
        pending_item.pending_transaction = PendingTransaction.objects.get(id=request.POST['pending_transaction'])
        pending_item.purchase_target = request.POST['purchase_target']
        pending_item.who_will_pay = request.POST['who_will_pay']
        pending_item.name = request.POST['name']
        pending_item.price = request.POST['price']
        pending_item.store = request.POST['store']
        pending_item.note = request.POST['note']
        pending_item.category = TransactionCategory.objects.get(id=request.POST['category'])
        pending_item.save()
        return HttpResponseRedirect(pending_item.get_update_link)
