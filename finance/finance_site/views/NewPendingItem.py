from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance_site.models.ItemModels import Item, PendingItem
from finance_site.models.TransactionModels import TransactionBase, TransactionCategory, PendingTransaction


class NewPendingItem(View):
    def get(self, request):
        pending_transactions = PendingTransaction.objects.filter(price__lt=0)
        return render(request, 'create_or_update_pending_item.html', context={
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     Item.who_will_pay_choices],
            "categories": TransactionCategory.objects.all(),
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
