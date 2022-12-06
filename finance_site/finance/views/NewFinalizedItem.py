from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.ItemModels import FinalizedItem
from finance.models.TransactionModels import FinalizedTransaction, TransactionCategory, TransactionBase


class NewFinalizedItem(View):
    def get(self, request):
        transaction_id = request.GET.get("transaction_id", None)
        if transaction_id is None:
            return HttpResponseRedirect("/")
        return render(request, 'create_or_update_finalized_item.html', context={
            "current_page": "create_finalized_item",
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     FinalizedItem.who_will_pay_choices],
            "categories": TransactionCategory.objects.all(),
            "finalize_transaction": FinalizedTransaction.objects.get(id=transaction_id),
            "finalized_transactions": FinalizedTransaction.objects.filter(price__lt=0).order_by('-date')
        })

    def post(self, request):
        transaction_id = request.GET.get("transaction_id", None)
        if transaction_id is None:
            return HttpResponseRedirect("/")
        finalized_item = FinalizedItem(
            name=request.POST['name'],
            price=request.POST['price'],
            purchase_target=request.POST['purchase_target'],
            who_will_pay=request.POST['who_will_pay'],
            category=TransactionCategory.objects.get(id=request.POST['category']),
            note=request.POST['note'],
            finalized_transaction=FinalizedTransaction.objects.get(id=request.GET['transaction_id']),
        )
        finalized_item.save()
        return HttpResponseRedirect(finalized_item.get_update_link)
