from django.db import models

from finance.models.TransactionModels import TransactionCategory, Transaction, PendingTransaction
from finance.urls import update_bank_item, update_pending_item


class ItemBase(models.Model):
    name = models.CharField(
        max_length=300
    )
    price = models.FloatField(

    )

    @property
    def formatted_price(self):
        return "$%.2f" % self.price

    purchase_target_choices = (
        ('Me', 'Me'),
        ('Dawn', 'Dawn'),
        ('Mircea', "Mircea")
    )
    purchase_target = models.CharField(
        max_length=50,
        choices=purchase_target_choices,
        default="Me"
    )
    waiting_for_reimbursement = models.BooleanField(
        default=False
    )

    who_will_pay_choices = (
        ('Me', 'Me'),  # if the responsibility for the purchase is ultimately me
        ('Vena', 'Vena'),  # if the responsibility for the purchase is ultimately Vena
        ('Micheal', 'Micheal'),  # if the responsibility for the purchase is ultimately Micheal
        ('Dawn', 'Dawn'),  # if the responsibility for the purchase is ultimately Dawn
    )

    who_will_pay = models.CharField(
        max_length=50,
        choices=who_will_pay_choices,
        default="Me"
    )
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE, null=True
    )
    note = models.CharField(
        max_length=300
    )


class Item(ItemBase):

    def get_transactions_refunding_this_item(self):
        return [
            transaction_refunding_item_mapping.refund_transaction
            for transaction_refunding_item_mapping in self.refunds_mapping_set.all()
            if transaction_refunding_item_mapping.original_item.id == self.id
        ]

    def get_transactions_reimbursing_this_item(self):
        return [
            transaction_reimbursing_item_mapping.reimbursement_transaction
            for transaction_reimbursing_item_mapping in self.reimbursements_mapping_set.all()
            if transaction_reimbursing_item_mapping.original_item.id == self.id
        ]

    def get_transaction_paying_back_this_item(self):
        return [
            transaction_paying_back_item_mapping.payback_transaction
            for transaction_paying_back_item_mapping in self.paybacks_mapping_set.all()
            if transaction_paying_back_item_mapping.original_item.id == self.id
        ]

    def get_labels(self):
        return [
            label_mapping.label
            for label_mapping in self.itemlabelintersection_set.all()
            if label_mapping.item.id == self.id
        ]

    @property
    def get_date(self):
        return self.transaction.get_date

    @property
    def get_month(self):
        return self.transaction.get_month

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    @property
    def get_update_link(self):
        return f"/{update_bank_item}{self.id}"

    def __str__(self):
        return f"ID [{self.id}] name [{self.name}] price [{self.price}] purchase_target [{self.purchase_target}] who_will_pay [{self.who_will_pay}] category [{self.category}] note [{self.note}]"


class PendingItem(ItemBase):
    pending_transaction = models.ForeignKey(PendingTransaction, on_delete=models.CASCADE)

    @property
    def get_update_link(self):
        return f"/{update_pending_item}{self.id}"

    def __str__(self):
        return f"ID [{self.id}] name [{self.name}] price [{self.price}] purchase_target [{self.purchase_target}] who_will_pay [{self.who_will_pay}] category [{self.category}] note [{self.note}]"

    pass


class ItemLabel(models.Model):
    label = models.CharField(
        max_length=300
    )
