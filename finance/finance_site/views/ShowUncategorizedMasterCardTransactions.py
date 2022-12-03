import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from querystring_parser import parser

from finance_site.models.TransactionModels import Transaction, TransactionCategory


class ShowUncategorizedMasterCardTransactions(View):
    def get(self, request):
        transactions = Transaction.objects.all().filter(payment_method="MasterCard").order_by(
            '-date')
        categories = TransactionCategory.objects.all()
        purchase_targets = [
            target[0]
            for target in Transaction.purchase_target_choices
        ]
        purchased_bys = [
            target[0]
            for target in Transaction.who_will_pay_choices
        ]
        uncategorized_transactions = []
        for transaction in transactions:
            if transaction.category is None and len(transaction.item_set.all()) == 0:
                uncategorized_transactions.append(transaction)

        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "transactions": uncategorized_transactions,
                "current_page": "uncategorized_mastercard",
                "categories": categories,
                "purchase_targets": purchase_targets,
                "purchased_bys": purchased_bys
            }
        )

    def post(self, request):
        print(1)
        un_categorized_transactions = list(parser.parse(request.POST.urlencode())['un_categorized_transaction'].values())
        for un_categorized_transaction in un_categorized_transactions:
            try:
                transaction = Transaction.objects.get(id=un_categorized_transaction['id'])
                transaction.month = un_categorized_transaction['month']
                transaction.who_will_pay = un_categorized_transaction['purchased_by']
                transaction.purchase_target = un_categorized_transaction['purchased_target']
                transaction.category = TransactionCategory.objects.get(id=un_categorized_transaction['category'])
                transaction.note = un_categorized_transaction['notes']
                transaction.save()
            except Exception:
                pass
            print(1)
        return HttpResponseRedirect("/uncategorized/mastercard")