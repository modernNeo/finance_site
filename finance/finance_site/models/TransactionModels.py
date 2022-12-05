import datetime

import pytz
from django.db import models

from finance_site.url_paths import update_pending_transaction
from finance_site.urls import update_bank_transaction


class TransactionCategory(models.Model):
    category = models.CharField(
        max_length=300,
        unique=True
    )

    def __str__(self):
        return self.category


class TransactionBase(models.Model):
    month = models.DateField(

    )

    @property
    def get_month(self):
        return self.month.strftime("%Y-%m")

    @property
    def get_front_end_month(self):
        return self.month.strftime("%Y-%m-%d")

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
        month_as_datetime_obj = datetime.datetime.strptime(f'{self.month.strftime("%Y-%m")}-01', "%Y-%m-%d").astimezone(
            vancouver_timezone) \
            if type(self.month) == datetime.datetime \
            else datetime.datetime.strptime(self.month, "%Y-%m-%d").astimezone(vancouver_timezone)
        self.month = datetime.datetime.strptime(
            f'{month_as_datetime_obj.strftime("%Y-%m")}-01', "%Y-%m-%d"
        ).astimezone(vancouver_timezone)

        super(TransactionBase, self).save(*args, **kwargs)

class Transaction(TransactionBase):
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE, null=True
    )

    def transaction_is_a_charge(self):
        refunded_receipt = self.get_transactions_this_transaction_is_refunding()
        reimbursements = self.get_transactions_that_are_reimbursing_this_transaction()
        paid_back_transaction = self.get_transactions_that_this_transaction_is_payback_for()
        return len(refunded_receipt) == 0 and len(reimbursements) == 0 and len(paid_back_transaction) == 0

    def get_transactions_refunding_this_transaction(self):
        return [
            refund.refund_transaction for refund in self.get_refund_transaction_set.all()
            if refund.original_transaction.id == self.id
        ]

    def get_transactions_this_transaction_is_refunding(self):
        return [
            original_receipt.original_transaction
            for original_receipt in self.get_original_transactions_set.all()
            if original_receipt.refund_transaction.id == self.id
        ]

    def get_any_etransfers_mapped_to_this_internal_transfer(self):
        return [
            etransfer_mapping.e_transfer
            for etransfer_mapping in self.get_corresponding_e_transfer_set.all()
            if etransfer_mapping.internal_transfer.id == self.id
        ]

    def get_any_internal_transfers_mapped_to_this_etransfer(self):
        return [
            internal_transfer_mapping.internal_transfer
            for internal_transfer_mapping in self.get_corresponding_internal_transfer_set.all()
            if internal_transfer_mapping.e_transfer.id == self.id
        ]

    def get_transactions_that_are_reimbursing_this_transaction(self):
        return [
            reimbursement_mapping.reimbursement_transaction
            for reimbursement_mapping in self.get_reimbursement_transactions_set.all()
            if reimbursement_mapping.original_transaction.id == self.id
        ]

    def get_receipts_that_this_transaction_is_a_reimbursement_for(self):
        return [
            reimbursement_mapping.original_transaction
            for reimbursement_mapping in self.get_original_transaction_set.all()
            if reimbursement_mapping.reimbursement_transaction.id == self.id
        ]

    def get_transactions_that_are_paying_back_this_transaction(self):
        return [
            payback_mapping.payback_transaction
            for payback_mapping in self.get_transaction_paying_back_this_transaction_set.all()
            if payback_mapping.original_transaction.id == self.id
        ]

    def get_transactions_that_this_transaction_is_payback_for(self):
        return [
            payback_mapping.original_transaction
            for payback_mapping in self.get_transaction_paying_back_this_transaction_set.all()
            if payback_mapping.payback_transaction.id == self.id
        ]

    @staticmethod
    def get_uncategorized_with_memo(date, method_of_transaction, name, memo, price):
        matching_uncategorized_bank_csv_transactions_draft = Transaction.objects.filter(
            date=date, method_of_transaction=method_of_transaction, name=name, memo=memo, price=price
        )
        matching_uncategorized_bank_csv_transactions = []
        for matching_uncategorized_bank_csv_transaction in matching_uncategorized_bank_csv_transactions_draft:
            if matching_uncategorized_bank_csv_transaction.category is None:
                if len(matching_uncategorized_bank_csv_transaction.item_set.all()) == 0:
                    matching_uncategorized_bank_csv_transactions.append(matching_uncategorized_bank_csv_transaction)
                elif len(matching_uncategorized_bank_csv_transaction.item_set.all()) > 0:
                    has_category = False
                    for item in matching_uncategorized_bank_csv_transaction.item_set.all():
                        has_category = has_category or item.category is not None
                    if not has_category:
                        matching_uncategorized_bank_csv_transactions.append(matching_uncategorized_bank_csv_transaction)
        return matching_uncategorized_bank_csv_transactions

    @property
    def get_update_link(self):
        return f"/{update_bank_transaction}{self.id}"

    def __str__(self):
        return f"Transaction [{self.id}] date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


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
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    label = models.ForeignKey(TransactionLabel, on_delete=models.CASCADE)
