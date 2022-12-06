from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.ItemModels import FinalizedItem
from finance.models.TransactionModels import TransactionBase, TransactionCategory


class UpdateFinalizedItem(View):
    def get(self, request, item_id):
        item = FinalizedItem.objects.get(id=item_id)
        return render(request, 'create_or_update_finalized_item.html', {
            "finalized_transaction": item.finalized_transaction,
            "item": item,
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     FinalizedItem.who_will_pay_choices],
            "categories": TransactionCategory.objects.all().order_by('order_number'),
            "transactions_refunding_item": item.get_transactions_refunding_this_item(),
            "transactions_reimbursing_item": item.get_transactions_reimbursing_this_item(),
            "transactions_paying_back_item": item.get_transaction_paying_back_this_item(),
            "labels": item.get_labels(),

        })

    def post(self, request, item_id):
        if request.POST['action'] == "update_item":
            item = FinalizedItem.objects.get(id=item_id)
            item.name = request.POST['name']
            item.price = request.POST['price']
            item.purchase_target = request.POST['purchase_target']
            item.who_will_pay = request.POST['who_will_pay']
            item.category = TransactionCategory.objects.get(id=request.POST['category']),
            item.note = request.POST['note']
            item.save()
            return HttpResponseRedirect(item.get_update_link)
        elif request.POST['action'] == "delete_item":
            is_finalized_item = hasattr(FinalizedItem.objects.get(id=item_id), "finalized_transaction")
            if is_finalized_item:
                payment_method = FinalizedItem.objects.get(id=item_id).finalized_transaction.payment_method
                if payment_method == "Debit Card":
                    return HttpResponseRedirect("/debit_card/all")
                else:
                    return HttpResponseRedirect("/master_card/all")
        return HttpResponseRedirect("/")
