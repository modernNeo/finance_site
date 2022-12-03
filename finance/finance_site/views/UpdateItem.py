from django.shortcuts import render
from django.views import View

from finance_site.models.ItemModels import Item
from finance_site.models.TransactionModels import TransactionBase, TransactionCategory


class UpdateItem(View):
    def get(self, request, item_id):
        item = Item.objects.get(id=item_id)
        transactions_refunding_item = item.get_transactions_refunding_this_item()
        transactions_reimbursing_item = item.get_transactions_reimbursing_this_item()
        transactions_paying_back_item = item.get_transaction_paying_back_this_item()
        labels = item.get_labels()
        return render(request, 'update_item.html', {
            "item": item,
            "payment_method_choices": [payment_choice[0] for payment_choice in TransactionBase.payment_method_choices],
            "purchase_target_choices": [purchase_target_choice[0] for purchase_target_choice in
                                        TransactionBase.purchase_target_choices],
            "who_will_pay_choices": [who_will_pay_choice[0] for who_will_pay_choice in
                                     Item.who_will_pay_choices],
            "categories": TransactionCategory.objects.all(),
            "transactions_refunding_item": transactions_refunding_item,
            "transactions_reimbursing_item": transactions_reimbursing_item,
            "transactions_paying_back_item": transactions_paying_back_item,
            "labels": labels,

        })
