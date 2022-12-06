from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.ItemModels import PendingItem, ItemBase
from finance.models.TransactionModels import PendingTransaction, TransactionCategory


class NewPendingItem(View):
    def get(self, request):
        pending_transactions = PendingTransaction.objects.filter(price__lt=0)
        return render(request, 'create_or_update_pending_item.html', context={
            "current_page": "create_pending_item",
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        ItemBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     ItemBase.who_will_pay_choices],
            "categories": TransactionCategory.objects.all().order_by('order_number'),
            "pending_transactions": pending_transactions
        })

    def post(self, request):
        pending_item = PendingItem(
            pending_transaction=PendingTransaction.objects.get(id=request.POST['pending_transaction']),
            purchase_target=request.POST['purchase_target'],
            who_will_pay=request.POST['who_will_pay'],
            price=request.POST.get('price', None),
            note=request.POST['note'],
            category=TransactionCategory.objects.get(id=request.POST['category']),
        )
        pending_item.save()
        return HttpResponseRedirect(pending_item.get_update_link)
