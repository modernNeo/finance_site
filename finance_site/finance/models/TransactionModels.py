import datetime

import pytz
from django.db import models

from finance.url_paths import update_pending_transaction, update_category
from finance.urls import update_finalized_transaction


class TransactionCategory(models.Model):
    category = models.CharField(
        max_length=300,
        unique=True
    )

    starred = models.BooleanField(
        default=False
    )

    order_number = models.IntegerField(
        unique=True,
        default=None,
        null=True
    )

    @property
    def get_update_link(self):
        return f"/{update_category}{self.id}"

    def __str__(self):
        return self.category


class TransactionBase(models.Model):
    month = models.DateField(
        null=True,
        default=None
    )

    @property
    def get_month(self):
        return self.month.strftime("%Y-%m") if self.month is not None else "None"

    @property
    def get_front_end_month(self):
        return self.month.strftime("%Y-%m-%d") if self.month is not None else "None"

    date = models.DateTimeField(

    )

    @property
    def get_front_end_date(self):
        return self.date.strftime("%Y-%m-%d")

    @property
    def get_date(self):
        return self.date.strftime("%Y-%m-%d")

    payment_method_choices = (
        ('MasterCard', 'MasterCard'),
        ('Debit Card', 'Debit Card'),
        ('Paid by Dawn', "Paid by Dawn"),  # if I have to reimburse Dawn for any purchases she made for me on her card
    )
    payment_method = models.CharField(
        max_length=50,
        choices=payment_method_choices,
        default='MasterCard',
    )
    purchase_target_choices = (
        ('Me', 'Me'),  # if the product is being used by me
        ('Dawn', 'Dawn'),  # if the product is being used by Dawn
        ('Mircea', "Mircea"),  # if the product will be used by Michero
        ("Group Purchase", "Group Purchase")
    )
    purchase_target = models.CharField(
        max_length=50,
        choices=purchase_target_choices,
        default="Me"
    )

    # Create your models here.
    who_will_pay_choices = (
        ('Me', 'Me'),  # if the responsibility for the purchase is ultimately me
        ('Vena', 'Vena'),  # if the responsibility for the purchase is ultimately Vena
        ('Micheal', 'Micheal'),  # if the responsibility for the purchase is ultimately Micheal
        ('Dawn', 'Dawn'),  # if the responsibility for the purchase is ultimately Dawn
        ("Group Purchase", "Group Purchase")
        # if its an transaction purchase and multiple people have to pay for each item
    )

    who_will_pay = models.CharField(
        max_length=50,
        choices=who_will_pay_choices,
        default="Me"
    )

    method_of_transaction_choices = (
        ('ATM', 'ATM'),
        ('Chequing', 'Chequing'),
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
        ('Other', 'Other'),
        ('POS', 'POS'),
    )
    method_of_transaction = models.CharField(
        max_length=200,
        choices=method_of_transaction_choices,
        default="Credit"
    )

    type_choices = (
        ('Charge', 'Charge'),
        ('Refund', 'Refund'),
        ('Payment', 'Payment')
    )
    type = models.CharField(
        max_length=200,
        choices=type_choices,
        default="Charge"
    )

    name = models.CharField(
        max_length=500
    )
    memo = models.CharField(
        max_length=500
    )
    price = models.FloatField(

    )

    @property
    def formatted_price(self):
        return "$%.2f" % self.price

    store = models.CharField(
        max_length=300
    )
    receipt = models.FileField(

    )
    note = models.CharField(
        max_length=300
    )
    processed = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs):
        if self.payment_method.lower() == "Mastercard".lower():
            self.payment_method = "MasterCard"
        elif self.payment_method.lower() == "Debit Card".lower():
            self.payment_method = "Debit Card"
            pass
        elif self.payment_method.lower() == "Paid by Dawn".lower():
            self.payment_method = "Paid by Dawn"
        else:
            raise Exception(f"Unknown payment method of {self.payment_method} detected")
        vancouver_timezone = pytz.timezone('America/Vancouver')
        if self.month is not None:
            month_as_datetime_obj = datetime.datetime.strptime(f'{self.month.strftime("%Y-%m")}-01', "%Y-%m-%d").astimezone(
                vancouver_timezone) \
                if type(self.month) == datetime.datetime \
                else datetime.datetime.strptime(f"{self.month}", "%Y-%m-%d").astimezone(vancouver_timezone)
            self.month = datetime.datetime.strptime(
                f'{month_as_datetime_obj.strftime("%Y-%m")}-01', "%Y-%m-%d"
            ).astimezone(vancouver_timezone)

        super(TransactionBase, self).save(*args, **kwargs)


class FinalizedTransaction(TransactionBase):
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE, null=True
    )

    def is_partially_refunded(self):
        items = self.finalizeditem_set.all()
        items_individually_refunded = False
        for item in items:
            items_individually_refunded = items_individually_refunded or len(item.refunds_mapping_set.all())
        return items_individually_refunded

    def is_fully_refunded(self):
        return len(self.refunds_mapping_set.all()) > 0

    def no_refunds_detected(self):
        return not self.is_partially_refunded() and not self.is_fully_refunded()

    def is_partially_reimbursed(self):
        items = self.finalizeditem_set.all()
        items_individually_reimbursed = False
        for item in items:
            items_individually_reimbursed = items_individually_reimbursed or len(item.reimbursements_mapping_set.all())
        return items_individually_reimbursed

    def is_fully_reimbursed(self):
        return len(self.reimbursements_mapping_set.all()) > 0

    def no_reimbursements_detected(self):
        return not self.is_partially_reimbursed() and not self.is_fully_reimbursed()

    def transaction_is_a_charge(self):
        refunded_receipt = self.get_transactions_this_transaction_is_refunding()
        reimbursements = self.get_transactions_this_transaction_is_reimbursing()
        paid_back_transaction = self.get_transaction_this_transaction_is_paying_back()
        return len(refunded_receipt) == 0 and len(reimbursements) == 0 and len(paid_back_transaction) == 0

    def get_transactions_this_transaction_is_refunding(self):
        return [
            transaction_refund_mapping.original_transaction
            for transaction_refund_mapping in self.refund_for_transaction_original_mapping_set.all()
            if transaction_refund_mapping.refund_transaction.id == self.id
        ]

    def get_transactions_this_transaction_is_reimbursing(self):
        return [
            transaction_reimbursement_mapping.original_transaction
            for transaction_reimbursement_mapping in self.reimbursement_for_transaction_original_mapping_set.all()
            if transaction_reimbursement_mapping.reimbursement_transaction.id == self.id
        ]

    def get_transaction_this_transaction_is_paying_back(self):
        return [
            transaction_payback_mapping.original_transaction
            for transaction_payback_mapping in self.payback_for_transaction_original_mapping_set.all()
            if transaction_payback_mapping.payback_transaction.id == self.id
        ]

    def get_transactions_reimbursing_this_transaction(self):
        return [
            reimbursement_mapping.reimbursement_transaction
            for reimbursement_mapping in self.reimbursements_mapping_set.all()
            if reimbursement_mapping.original_transaction.id == self.id
        ]

    def get_transactions_refunding_this_transaction(self):
        return [
            refund_mapping.refund_transaction
            for refund_mapping in self.refunds_mapping_set.all()
            if refund_mapping.original_transaction.id == self.id
        ]

    def get_transactions_paying_back_this_transaction(self):
        return [
            payback_mapping.payback_transaction
            for payback_mapping in self.paybacks_mapping_set.all()
            if payback_mapping.original_transaction.id == self.id
        ]

    def get_any_etransfers_mapped_to_this_internal_transfer(self):
        return [
            etransfer_mapping.e_transfer
            for etransfer_mapping in self.corresponding_e_transfer_mapping_set.all()
            if etransfer_mapping.internal_transfer.id == self.id
        ]

    def get_any_internal_transfers_mapped_to_this_etransfer(self):
        return [
            internal_transfer_mapping.internal_transfer
            for internal_transfer_mapping in self.corresponding_internal_transfer_mapping_set.all()
            if internal_transfer_mapping.e_transfer.id == self.id
        ]

    @staticmethod
    def get_uncategorized_with_memo(date, method_of_transaction, name, memo, price):
        matching_uncategorized_finalized_transactions_draft = FinalizedTransaction.objects.filter(
            date=date, method_of_transaction=method_of_transaction, name=name, memo=memo, price=price
        )
        matching_uncategorized_finalized_transactions = []
        for matching_uncategorized_finalized_transaction in matching_uncategorized_finalized_transactions_draft:
            if matching_uncategorized_finalized_transaction.category is None:
                if len(matching_uncategorized_finalized_transaction.finalizeditem_set.all()) == 0:
                    matching_uncategorized_finalized_transactions.append(matching_uncategorized_finalized_transaction)
                elif len(matching_uncategorized_finalized_transaction.finalizeditem_set.all()) > 0:
                    has_category = False
                    for item in matching_uncategorized_finalized_transaction.finalizeditem_set.all():
                        has_category = has_category or item.category is not None
                    if not has_category:
                        matching_uncategorized_finalized_transactions.append(matching_uncategorized_finalized_transaction)
        return matching_uncategorized_finalized_transactions

    @property
    def get_update_link(self):
        return f"/{update_finalized_transaction}{self.id}"

    def __str__(self):
        return f"FinalizedTransaction [{self.id}] date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


class LegacyTransaction(TransactionBase):
    category = models.CharField(
        max_length=300
    )

    def __str__(self):
        return f"LegacyTransaction date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


class PendingTransaction(TransactionBase):
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE
    )

    @property
    def get_update_link(self):
        return f"/{update_pending_transaction}{self.id}"

    def __str__(self):
        return f"PendingTransaction date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


class TransactionLabel(models.Model):
    label = models.CharField(
        max_length=300
    )


class TransactionLabelIntersection(models.Model):
    transaction = models.ForeignKey(FinalizedTransaction, on_delete=models.CASCADE)
    label = models.ForeignKey(TransactionLabel, on_delete=models.CASCADE)
