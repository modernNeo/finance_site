import datetime

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance_site.models.TransactionModels import Transaction, LegacyTransaction, \
    TransactionCategory


class ShowUnTransferredLegacyMasterCardTransactions(View):
    def get(self, request):
        request_path = request.path

        current_page = request.GET.get('p', 'none')
        if current_page == 'none':
            current_page = 1
        else:
            current_page = int(current_page)
        unlinked_bank_csv_transactions = Transaction.objects.all().filter(category__isnull=True)
        paginated_object = Paginator(
            LegacyTransaction.objects.all()
            .filter(payment_method="MasterCard",date__gte=datetime.datetime.strptime("2021-12-01", "%Y-%m-%d"))
            .order_by('-date'),
            per_page=100
        )
        if paginated_object.num_pages < current_page:
            return HttpResponseRedirect(request_path)

        legacy_transaction_details_csv_transactions = paginated_object.page(current_page)

        previous_button_link = request_path + '?p=' + str(
            current_page - 1 if current_page > 1 else paginated_object.num_pages
        )
        next_button_link = request_path + '?p=' + str(
            current_page + 1 if current_page + 1 <= paginated_object.num_pages else 1
        )
        return render(
            request, 'un_transferred_legacy_transactions.html',
            context={
                "legacy_transaction_details_csv_transactions": legacy_transaction_details_csv_transactions,
                "unlinked_transactions": unlinked_bank_csv_transactions,
                "current_page": "un_transferred_legacy_mastercard",
                'nextButtonLink': next_button_link,
                'previousButtonLink': previous_button_link,

            }
        )

    def post(self, request):
        unfinalized_legacy_transactions = list(
            (parser.parse(request.POST.urlencode()))['legacy_transaction_details_csv_transactions'].values()
        )
        unfinalized_legacy_transactions = [
            unfinalized_legacy_transaction
            for unfinalized_legacy_transaction in unfinalized_legacy_transactions
            if unfinalized_legacy_transaction["bank_transaction"] != "None"
        ]
        unlinked_bank_csv_transactions = Transaction.objects.all().filter(category__isnull=True)
        for unfinalized_legacy_transaction in unfinalized_legacy_transactions:
            # {'id': '1275', 'payment_method': 'MASTERCARD', 'name': 'DONALDS MARKET VANCOUVER BC',
            #  'memo': 'Rewards earned: 2.20 ~ Category: Groceries', 'store': '', 'category': 'Household Necessity'}
            print(unfinalized_legacy_transaction)
            matching_bank_csv_transaction = unlinked_bank_csv_transactions.get(
                id=int(unfinalized_legacy_transaction['bank_transaction'])
            )
            matching_bank_csv_transaction.category = TransactionCategory.objects.get(
                category=unfinalized_legacy_transaction['category']
            )
            matching_bank_csv_transaction.save()
            LegacyTransaction.objects.get(id=int(unfinalized_legacy_transaction['id'])).delete()
        legacy_transaction_details_csv_transactions = LegacyTransaction.objects.all()
        return render(
            request, 'unfinalized_transactions.html',
            context={
                "legacy_transaction_details_csv_transactions": legacy_transaction_details_csv_transactions,
                "unlinked_transactions": unlinked_bank_csv_transactions,
                "current_page": "un_transferred_legacy_mastercard"
            }
        )