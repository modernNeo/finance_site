from django.db import models

from finance_site.models.ItemModels import Item, ItemLabel
from finance_site.models.TransactionModels import Transaction


# for when a transaction like from cineplex gets refunded
class TransactionRefund(models.Model):
    original_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_refund_transaction_set'
    )
    refund_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_transactions_set'
    )

    @property
    def get_update_link(self):
        return f"/mapping/refund/transaction/update/{self.id}"


# for I get reimbursed for like health care from Vena or something
class TransactionReimbursement(models.Model):
    original_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_reimbursement_transactions_set'
    )
    reimbursement_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_transaction_set'
    )
    note = models.CharField(
        max_length=500
    )

    @property
    def get_update_link(self):
        return f"/mapping/reimbursement/transaction/update/{self.id}"


# for when Mircea or Dawn pay me back for a whole transaction
class TransactionPayBack(models.Model):
    original_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_transaction_paying_back_this_transaction_set'
    )
    payback_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_transaction_being_paid_back_set'
    )
    note = models.CharField(
        max_length=500
    )

    @property
    def get_update_link(self):
        return f"/mapping/repaid/transaction/update/{self.id}"


# for when an item like from donalds gets refunded
class ItemRefund(models.Model):
    original_item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        related_name='get_item_refund_transaction_set'
    )
    refund_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_refunded_item_set'
    )

    @property
    def get_update_link(self):
        return f"/mapping/refund/item/update/{self.id}"


# if a particular items gets reimbursed by someone like Vena [team lunch]
class ItemReimbursement(models.Model):
    original_item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        related_name='get_item_reimbursement_transactions_set'
    )
    reimbursement_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_reimbursed_item_set'
    )
    note = models.CharField(
        max_length=500,
        null=True
    )

    @property
    def get_update_link(self):
        return f"/mapping/reimbursement/item/update/{self.id}"


# for when Mircea or Dawn pay me back for a particular item in a transaction
class ItemPayBack(models.Model):
    original_item = models.ForeignKey(
        Item, on_delete=models.CASCADE,
        related_name='get_transaction_paying_back_item_set'
    )
    payback_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_original_item_being_paid_back_set'
    )
    note = models.CharField(
        max_length=500
    )

    @property
    def get_update_link(self):
        return f"/mapping/repaid/item/update/{self.id}"


class ETransferToInternalTransferMapping(models.Model):
    e_transfer = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_corresponding_internal_transfer_set'
    )
    internal_transfer = models.ForeignKey(
        Transaction, on_delete=models.CASCADE,
        related_name='get_corresponding_e_transfer_set'
    )

    @property
    def get_update_link(self):
        return f"/mapping/e_transfer_internal_transfer_mapping/update/{self.id}"


class ItemLabelIntersection(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    label = models.ForeignKey(ItemLabel, on_delete=models.CASCADE)
