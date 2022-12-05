from django.db import models

from finance_site.models.TransactionModels import TransactionCategory, Transaction, PendingTransaction
from finance_site.urls import update_bank_item, update_pending_item


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
        list1= [
            transaction_refunding_item.refund_transaction
            for transaction_refunding_item in self.get_item_refund_transaction_set.all()
            if transaction_refunding_item.original_item.id == self.id
        ]
        list1.extend([
            transaction_refunding_overall_transaction
            for transaction_refunding_overall_transaction in self.transaction.get_transactions_refunding_this_transaction()
            ## still have to nail down the code that can differentiate between transactions refunding whole original
            ## transaction and transactions refunding only parts of original transaction
        ])
        return list1

    def get_transactions_reimbursing_this_item(self):
        list1= [
            transaction_reimbursing_item.reimbursement_transaction
            for transaction_reimbursing_item in self.get_item_reimbursement_transactions_set.all()
            if transaction_reimbursing_item.original_item.id == self.id
        ]
        list1.extend([
            transaction_refunding_overall_transaction
            for transaction_refunding_overall_transaction in self.transaction.get_transactions_that_are_reimbursing_this_transaction()
            ## still have to nail down the code that can differentiate between transactions refunding whole original
            ## transaction and transactions refunding only parts of original transaction
        ])
        return list1

    def get_transaction_paying_back_this_item(self):
        list1 = [
            transaction_paying_back_this_item.payback_transaction
            for transaction_paying_back_this_item in self.get_transaction_paying_back_item_set.all()
            if transaction_paying_back_this_item.original_item.id == self.id
        ]
        list1.extend([
            transaction_payingback_overall_transaction
            for transaction_payingback_overall_transaction in self.transaction.get_transaction_paying_back_this_transaction_set.all()
            ## still have to nail down the code that can differentiate between transactions refunding whole original
            ## transaction and transactions refunding only parts of original transaction
        ])
        return list1

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
