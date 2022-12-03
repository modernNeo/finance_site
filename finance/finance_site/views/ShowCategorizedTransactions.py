from django.shortcuts import render
from django.views.generic.base import View

from finance_site.models.TransactionModels import Transaction


class ShowCategorizedTransactions(View):
    def get(self, request):
        transactions = Transaction.objects.all().filter(category__isnull=False).order_by('-date')
        months = list(set([transaction.get_month for transaction in transactions]))
        months.sort()
        months = list(reversed(months))
        categorized_transactions = {}
        category_totals = {}
        categories_i_care_about = [
            "Numeris",
            "Government Deposit",
            "Misc Income",
            "Rent",
            "Beauty/Vanity",
            "Chomp",
            "Household Necessities",
            "Homeless People",
            "Spanish Tutoring",
            "Pho Friday",
            "Yearly Subscription",
            "Recurring Monthly Bills",
            "Charity Donations",
            "Music/Movies",
            "Leisure",
            "Online Purchases",
            "Theatres/New DVD releases",
            "Home-Office",
            "Medical",
            "Automated Student Loans Payment",
            "Student Loans"
        ]
        for transaction in transactions:
            if transaction.category is not None:
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(transaction)
                da_item = transaction
                if da_item.category.category in categories_i_care_about:
                    if da_item.get_month not in category_totals:
                        category_totals[da_item.get_month] = {}
                    if da_item.category.category not in category_totals[da_item.get_month]:
                        category_totals[da_item.get_month][da_item.category.category] = 0
                    category_totals[da_item.get_month][da_item.category.category] += da_item.price
                if transaction.category.category == "Partial" or transaction.category.category == "Categorized Elsewhere":
                    for item in transaction.item_set.all():
                        if transaction.get_month not in categorized_transactions:
                            categorized_transactions[transaction.get_month] = []
                        categorized_transactions[transaction.get_month].append(item)
                        da_item = item
                        if da_item.category.category in categories_i_care_about:
                            if da_item.get_month not in category_totals:
                                category_totals[da_item.get_month] = {}
                            if da_item.category.category not in category_totals[da_item.get_month]:
                                category_totals[da_item.get_month][da_item.category.category] = 0
                            category_totals[da_item.get_month][da_item.category.category] += da_item.price
                        for reimbursement_receipt in item.get_item_reimbursement_transactions_set.all():
                            if transaction.get_month not in categorized_transactions:
                                categorized_transactions[transaction.get_month] = []
                            categorized_transactions[transaction.get_month].append(
                                reimbursement_receipt.reimbursement_transaction)
                            da_item = reimbursement_receipt.reimbursement_transaction
                            if da_item.category.category in categories_i_care_about:
                                if da_item.get_month not in category_totals:
                                    category_totals[da_item.get_month] = {}
                                if da_item.category.category not in category_totals[da_item.get_month]:
                                    category_totals[da_item.get_month][da_item.category.category] = 0
                                category_totals[da_item.get_month][da_item.category.category] += da_item.price
            refunds_receipt = transaction.get_transactions_refunding_this_transaction()
            for refund_receipt in refunds_receipt:
                refund_receipt.pre_pend = "--REFUND BY--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(refund_receipt)
                da_item = refund_receipt
                if da_item.category.category in categories_i_care_about:
                    if da_item.get_month not in category_totals:
                        category_totals[da_item.get_month] = {}
                    if da_item.category.category not in category_totals[da_item.get_month]:
                        category_totals[da_item.get_month][da_item.category.category] = 0
                    category_totals[da_item.get_month][da_item.category.category] += da_item.price
            original_receipts = transaction.get_transactions_this_transaction_is_refunding()
            for original_receipt in original_receipts:
                original_receipt.pre_pend = "--REFUNDS--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(original_receipt)
                da_item = original_receipt
                if da_item.category.category in categories_i_care_about:
                    if da_item.get_month not in category_totals:
                        category_totals[da_item.get_month] = {}
                    if da_item.category.category not in category_totals[da_item.get_month]:
                        category_totals[da_item.get_month][da_item.category.category] = 0
                    category_totals[da_item.get_month][da_item.category.category] += da_item.price

            corresponding_internal_transfers = transaction.get_corresponding_internal_transfer_set.all()
            for corresponding_internal_transfer in corresponding_internal_transfers:
                corresponding_internal_transfer.internal_transfer.pre_pend = "--Corr. Int. Trnsfer--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(
                    corresponding_internal_transfer.internal_transfer)
                da_item = corresponding_internal_transfer.internal_transfer
                if da_item.category.category in categories_i_care_about:
                    if da_item.get_month not in category_totals:
                        category_totals[da_item.get_month] = {}
                    if da_item.category.category not in category_totals[da_item.get_month]:
                        category_totals[da_item.get_month][da_item.category.category] = 0
                    category_totals[da_item.get_month][da_item.category.category] += da_item.price

            corresponding_etransfers = transaction.get_corresponding_e_transfer_set.all()
            for corresponding_etransfer in corresponding_etransfers:
                corresponding_etransfer.e_transfer.pre_pend = "--Corr. ETrnsfer--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(corresponding_etransfer.e_transfer)
                da_item = corresponding_etransfer.e_transfer
                if da_item.category.category in categories_i_care_about:
                    if da_item.get_month not in category_totals:
                        category_totals[da_item.get_month] = {}
                    if da_item.category.category not in category_totals[da_item.get_month]:
                        category_totals[da_item.get_month][da_item.category.category] = 0
                    category_totals[da_item.get_month][da_item.category.category] += da_item.price

        for month, value in category_totals.items():
            for category, price in value.items():
                category_totals[month][category] = "$%.2f" % price

        return render(
            request, 'index.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "category_totals": category_totals,
                "current_page": "categorized",
                "months": months,
                "current_month": "2022-11"
            }
        )
