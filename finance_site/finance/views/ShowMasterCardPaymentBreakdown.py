import datetime
import json

from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import FinalizedTransaction


class ShowMasterCardPaymentBreakdown(View):
    def get(self, request):
        transactions = FinalizedTransaction.objects.all().filter(category__isnull=False, payment_method="MasterCard").order_by(
            '-date')
        months = list(set([transaction.get_month for transaction in transactions]))
        months.sort()
        months = list(reversed(months))
        mastercard_expenses = {
            # "month": {
            #     "<category>": {
            #         "total_price": 0,
            #         "transactions": [
            #             # //do not include transaction that are repayments/reimbursements/refunding a specific item below, otherwise, they are counted twice
            #             {
            #                 "type": "regular_transaction"
            #                 "transaction" : transaction
            #             },
            #             {
            #                 "original_transaction": "transaction",
            #                 "refund": "refund_transaction"
            #             },
            #             {
            #                 "original_transaction": "transaction",
            #                 "reimbursement": "reimbursement_transaction"
            #             },
            #             {
            #                 "original_transaction": "transaction",
            #                 "repayment": "repayment_transaction"
            #             },
            #
            #         ],
            #         "items": [
            #             {
            #                 "original_item": "item",
            #                 "refund": "refund_transaction"
            #             },
            #             {
            #                 "original_item": "item",
            #                 "reimbursement": "reimbursement_item"
            #             },
            #             {
            #                 "original_item": "item",
            #                 "repayment": "repayment_item"
            #             },
            #         ]
            #     },
            #     "partial": {
            #         # don't need to include the transactions that the items are filed under, because if I have done
            #         # the mapping correctly, the items will in total cover the total cast
            #         # the below items should really only be the items that I bought for other people. everything else
            #         # should be covered under the specific categories that pertain to me
            #         "total_price": 0,
            #         "items": [
            #             {
            #                 "original_item": "item",
            #                 "refund": "refund"
            #             },
            #             {
            #                 "original_item": "transaction",
            #                 "reimbursement": "reimbursement"
            #             },
            #             {
            #                 "original_item": "transaction",
            #                 "repayment": "repayment"
            #             },
            #         ]
            #     }
            # }
        }
        refunds_already_added_to_calculation = []
        reimbursements_already_added_to_calculation = []
        for transaction in transactions:
            if transaction.transaction_is_a_charge():
                if transaction.is_fully_refunded() or transaction.is_fully_reimbursed():
                    refunds = transaction.get_transactions_refunding_this_transaction()
                    reimbursements = transaction.get_transactions_reimbursing_this_transaction()
                    if len(refunds) > 0:
                        add_refund_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction,
                            refunds
                        )
                    elif len(reimbursements) > 0:
                        add_reimbursement_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction,
                            reimbursements
                        )
                elif transaction.category.category == "Partial":
                    for item in transaction.finalizeditem_set.all():
                        if item.category.category == "Not My Expense":
                            # these are all other people's expenses
                            refunds = item.get_transactions_refunding_this_item()
                            reimbursements = item.get_transactions_reimbursing_this_item()
                            paybacks = item.get_transaction_paying_back_this_item()
                            item_was_never_revoked = len(refunds) == 0 and len(reimbursements) == 0 and len(
                                paybacks) == 0
                            if item_was_never_revoked:
                                add_unrevoked_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item
                                )
                            elif len(refunds) > 0:
                                add_refunded_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item, refunds
                                )

                            elif len(reimbursements) > 0:
                                add_reimbursed_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item,
                                    reimbursements
                                )
                            elif len(paybacks) > 0:
                                add_paid_back_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item, paybacks
                                )
                        else:
                            # these are all my portion of "Partial" transactions
                            refunds = item.get_transactions_refunding_this_item()
                            reimbursements = item.get_transactions_reimbursing_this_item()
                            paybacks = item.get_transaction_paying_back_this_item()

                            item_was_never_revoked = len(refunds) == 0 and len(reimbursements) == 0 and len(
                                paybacks) == 0
                            if item_was_never_revoked:
                                add_unrevoked_item(mastercard_expenses, item.get_month, item.category.category, item)
                            elif len(refunds) > 0:
                                add_refunded_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item, refunds,
                                )
                            elif len(reimbursements) > 0:
                                add_reimbursed_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item,
                                    reimbursements
                                )
                            elif len(paybacks) > 0:
                                add_paid_back_item(
                                    mastercard_expenses, transaction.get_month, item.category.category, item, paybacks
                                )
                else:
                    ## covers transactions that are wholly paid by me
                    refunds = transaction.get_transactions_refunding_this_transaction()
                    reimbursements = transaction.get_transactions_paying_back_this_transaction()
                    paybacks = transaction.paybacks_mapping_set.all()
                    transaction_was_never_revoked = len(refunds) == 0 and len(reimbursements) == 0 and len(
                        paybacks) == 0
                    if transaction_was_never_revoked:
                        add_regular_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction
                        )
                    elif len(refunds) > 0:
                        add_refund_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction,
                            refunds
                        )
                    elif len(reimbursements) > 0:
                        add_reimbursement_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction,
                            reimbursements
                        )
                    elif len(paybacks) > 0:
                        add_paid_back_transaction(
                            mastercard_expenses, transaction.get_month, transaction.category.category, transaction,
                            paybacks
                        )
        return render(
            request, 'payment_breakdown.html',
            context={
                "mastercard_expenses": mastercard_expenses,
                "current_page": "payment_breakdown",
                "months": months,
                "current_month": datetime.datetime.now().strftime("%Y-%m"),
            }
        )


def add_category_to_expenses_dict(mastercard_expenses, month, category):
    if month not in mastercard_expenses:
        mastercard_expenses[month] = {}
    if category not in mastercard_expenses[month]:
        mastercard_expenses[month][category] = {
            "total_price": 0.0,
            "transactions": [],
            "items": []
        }


def add_regular_transaction(mastercard_expenses, month, category, transaction):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    mastercard_expenses[month][category]['total_price'] += transaction.price
    mastercard_expenses[month][category]['transactions'].append(
        {
            "type": "regular_transaction",
            "transaction": transaction
        })


def add_reimbursement_transaction(mastercard_expenses, month, category, transaction, reimbursements):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    price = transaction.price
    for reimbursement in reimbursements:
        price += reimbursement.price
    mastercard_expenses[month][category]['total_price'] -= price
    mastercard_expenses[month][category]['transactions'].append(
        {
            "type": "reimbursed_transaction" if len(reimbursements) > 0 else "awaiting_reimbursement",
            "transaction": transaction,
            "reimbursements": reimbursements
        }
    )


def add_paid_back_transaction(mastercard_expenses, month, category, transaction, paybacks):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    mastercard_expenses[month][category]['total_price'] -= transaction.price
    mastercard_expenses[month][category]['transactions'].append(
        {
            "type": "paid_back_transaction" if len(paybacks) > 0 else "awaiting_payback",
            "transaction": transaction,
            "paybacks": paybacks
        }
    )


def add_refund_transaction(mastercard_expenses, month, category, transaction, refunds):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    price = transaction.price
    for refund in refunds:
        price += refund.price
    mastercard_expenses[month][category]['total_price'] -= price
    mastercard_expenses[month][category]['transactions'].append(
        {
            "type": "refunded_transaction" if len(refunds) > 0 else "awaiting_refund",
            "transaction": transaction,
            "refunds": refunds
        }
    )


def add_unrevoked_item(mastercard_expenses, month, category, item):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    mastercard_expenses[month][category]['total_price'] += item.price
    mastercard_expenses[month][category]['items'].append(
        {
            "type": "regular_item",
            "item": item
        }
    )


def add_refunded_item(mastercard_expenses, month, category, item, refunds):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    price = item.price
    for refund in refunds:
        price += refund.price
    mastercard_expenses[month][category]['total_price'] += price
    mastercard_expenses[month][category]['items'].append(
        {
            "type": "refunded_item" if len(refunds) > 0 else "waiting_refund",
            "item": item,
            "refunds": refunds
        }
    )


def add_reimbursed_item(mastercard_expenses, month, category, item, reimbursements):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    price = item.price
    for reimbursement in reimbursements:
        price += reimbursement.price
    mastercard_expenses[month][category]['total_price'] += price
    mastercard_expenses[month][category]['items'].append(
        {
            "type": "reimbursed_item" if len(reimbursements) > 0 else "waiting_reimbursement",
            "item": item,
            "reimbursement": reimbursements
        }
    )


def add_paid_back_item(mastercard_expenses, month, category, item, pay_backs):
    add_category_to_expenses_dict(mastercard_expenses, month, category)
    mastercard_expenses[month][category]['total_price'] += item.price
    mastercard_expenses[month][category]['items'].append(
        {
            "type": "repaid_item" if len(pay_backs) > 0 else "waiting_repayment",
            "item": item,
            "pay_backs": pay_backs
        }
    )
