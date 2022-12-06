import datetime

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from querystring_parser import parser

from finance.models.TransactionModels import FinalizedTransaction, LegacyTransaction, \
    TransactionCategory


class ShowUnTransferredLegacyDebitCardTransactions(View):
    def get(self, request):
        request_path = request.path

        current_page = request.GET.get('p', 'none')
        if current_page == 'none':
            current_page = 1
        else:
            current_page = int(current_page)
        unlinked_finalized_transactions = FinalizedTransaction.objects.all().filter(category__isnull=True).order_by('-date')
        paginated_object = Paginator(
            LegacyTransaction.objects.all()
            .filter(payment_method="Debit Card",date__gte=datetime.datetime.strptime("2021-12-01", "%Y-%m-%d"))
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
                "unlinked_transactions": unlinked_finalized_transactions,
                "current_page": "un_transferred_legacy_debitcard",
                'nextButtonLink': next_button_link,
                'previousButtonLink': previous_button_link,

            }
        )