import datetime

from django.shortcuts import render
from django.views.generic.base import View

from finance.models.TransactionModels import FinalizedTransaction, TransactionCategory


class ShowCategorizedTransactions(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(category__isnull=False).order_by('-date')
        months = list(set([transaction.get_month for transaction in transactions]))
        months.sort()
        months = list(reversed(months))
        categorized_transactions = {}
        draft_category_totals = {}
        categories_i_care_about = list(
            TransactionCategory.objects.all().order_by('order_number').values_list("category", flat=True)
        )

        for transaction in transactions:
            if transaction.category is not None:
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(transaction)
                if transaction.category.category in categories_i_care_about:
                    increase_price(draft_category_totals, transaction.get_month,
                                   transaction.category.category, transaction.price)
                if transaction.category.category == "Partial" or transaction.category.category == "Categorized Elsewhere":
                    for item in transaction.finalizeditem_set.all():
                        if transaction.get_month not in categorized_transactions:
                            categorized_transactions[transaction.get_month] = []
                        categorized_transactions[transaction.get_month].append(item)
                        if item.category.category in categories_i_care_about:
                            increase_price(draft_category_totals, item.get_month, item.category.category,
                                           item.price)
                        for reimbursement_receipt in item.reimbursements_mapping_set.all():
                            if transaction.get_month not in categorized_transactions:
                                categorized_transactions[transaction.get_month] = []
                            categorized_transactions[transaction.get_month].append(
                                reimbursement_receipt.reimbursement_transaction)
                            reimbursement_transaction = reimbursement_receipt.reimbursement_transaction
                            if reimbursement_transaction.category.category in categories_i_care_about:
                                increase_price(
                                    draft_category_totals,
                                    reimbursement_transaction.get_month,
                                    reimbursement_transaction.category.category,
                                    reimbursement_transaction.price
                                )
            refunds_receipt = transaction.get_transactions_refunding_this_transaction()
            for refund_receipt in refunds_receipt:
                refund_receipt.pre_pend = "--REFUND BY--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(refund_receipt)
                if refund_receipt.category.category in categories_i_care_about:
                    increase_price(draft_category_totals, refund_receipt.get_month,
                                   refund_receipt.category.category, refund_receipt.price)
            original_receipts = transaction.get_transactions_this_transaction_is_refunding()
            for original_receipt in original_receipts:
                original_receipt.pre_pend = "--REFUNDS--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(original_receipt)
                if original_receipt.category.category in categories_i_care_about:
                    increase_price(draft_category_totals, original_receipt.get_month,
                                   original_receipt.category.category, original_receipt.price)

            corresponding_internal_transfers = transaction.corresponding_internal_transfer_mapping_set.all()
            for corresponding_internal_transfer in corresponding_internal_transfers:
                corresponding_internal_transfer.internal_transfer.pre_pend = "--Corr. Int. Trnsfer--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(
                    corresponding_internal_transfer.internal_transfer)
                internal_transfer = corresponding_internal_transfer.internal_transfer
                if internal_transfer.category.category in categories_i_care_about:
                    increase_price(
                        draft_category_totals, internal_transfer.get_month,
                        internal_transfer.category.category,
                        internal_transfer.price
                    )

            corresponding_etransfers = transaction.corresponding_e_transfer_mapping_set.all()
            for corresponding_etransfer in corresponding_etransfers:
                corresponding_etransfer.e_transfer.pre_pend = "--Corr. ETrnsfer--"
                if transaction.get_month not in categorized_transactions:
                    categorized_transactions[transaction.get_month] = []
                categorized_transactions[transaction.get_month].append(corresponding_etransfer.e_transfer)
                e_transfer = corresponding_etransfer.e_transfer
                if e_transfer.category.category in categories_i_care_about:
                    increase_price(
                        draft_category_totals, e_transfer.get_month, e_transfer.category.category,
                        e_transfer.price
                    )
        final_category_totals = {}
        for month, categories in draft_category_totals.items():
            final_category_totals[month] = []
            row = 0
            for category, price, in categories.items():
                if price != 0:
                    if len(final_category_totals[month]) == 0:
                        final_category_totals[month].append([{category: "$%.2f" % price}])
                    elif len(final_category_totals[month]) == row:
                        final_category_totals[month].append([[{category: "$%.2f" % price}]])
                    else:
                        final_category_totals[month][row].append({category: "$%.2f" % price})
                    if len(final_category_totals[month][row]) == 5:
                        row += 1

        return render(
            request, 'show_categorized_transactions.html', context=
            {
                "categorized_transactions": categorized_transactions,
                "category_totals": final_category_totals,
                "current_page": "categorized",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m"),
            }
        )


def increase_price(category_dict, month_str, category_str, price):
    if month_str not in category_dict:
        category_dict[month_str] = {}
        for category in TransactionCategory.objects.all().order_by('order_number'):
            category_dict[month_str][category.category] = 0
    category_dict[month_str][category_str] += price
