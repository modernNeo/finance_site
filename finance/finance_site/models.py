from django.db import models


# Create your models here.


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

    date = models.DateTimeField(

    )

    @property
    def get_date(self):
        return self.date.strftime("%Y-%m-%d")

    payment_method_choices = (
        ('Mastercard', 'Mastercard'),
        ('Debit Card', 'Debit Card'),
        ('Paid by Dawn', "Paid by Dawn"),  # if I have to reimburse Dawn for any purchases she made for me on her card
    )
    payment_method = models.CharField(
        max_length=50,
        choices=payment_method_choices,
        default='Mastercard',
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

    who_will_pay_choices = (
        ('Me', 'Me'),  # if the responsibility for the purchase is ultimately me
        ('Vena', 'Vena'),  # if the responsibility for the purchase is ultimately Vena
        ('Micheal', 'Micheal'),  # if the responsibility for the purchase is ultimately Micheal
        ('Dawn', 'Dawn')  # if the responsibility for the purchase is ultimately Dawn
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
    store = models.CharField(
        max_length=300
    )
    receipt = models.FileField(

    )
    note = models.CharField(
        max_length=300
    )

    def save(self, *args, **kwargs):
        if self.payment_method.lower() == "Mastercard".lower():
            if self.method_of_transaction == "DEBIT":
                self.type = "Charge"
            elif self.method_of_transaction == "CREDIT":
                if self.name == 'PAYMENT - THANK YOU':
                    self.type = 'Payment'
                else:
                    self.type = "Refund"
            else:
                raise Exception(f"Unknown method_of_transaction of {self.method_of_transaction} detected")
        else:
            raise Exception(f"Unknown payment method of {self.payment_method} detected")

        super(TransactionBase, self).save(*args, **kwargs)


class BankCSVTransaction(TransactionBase):
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE, null=True
    )

    def get_refund_receipts(self):
        return [
            refund.refund_transaction_in_refund for refund in self.get_refund_receipts_set.all()
            if refund.refund_transaction_in_refund.id != self.id
        ]

    def get_original_receipts(self):
        return [
            original_receipt.original_transaction_in_refund
            for original_receipt in self.get_original_receipts_set.all()
            if original_receipt.original_transaction_in_refund.id != self.id
        ]

    @staticmethod
    def get_uncategorized_with_memo(date, method_of_transaction, name, memo, price):
        matching_uncategorized_bank_csv_transactions_draft = BankCSVTransaction.objects.filter(
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

    @staticmethod
    def get_uncategorized_without_memo(date, method_of_transaction, name, price):
        matching_uncategorized_bank_csv_transactions_draft = BankCSVTransaction.objects.filter(
            date=date, method_of_transaction=method_of_transaction, name=name, price=price
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

    def __str__(self):
        return f"BankCSVTransaction date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


class ReceiptRefund(models.Model):
    original_transaction_in_refund = models.ForeignKey(
        BankCSVTransaction, on_delete=models.CASCADE,
        related_name='get_refund_receipts_set'
    )
    refund_transaction_in_refund = models.ForeignKey(
        BankCSVTransaction, on_delete=models.CASCADE,
        related_name='get_original_receipts_set'
    )


class ReimbursementTransaction(models.Model):
    original_transaction = models.ForeignKey(
        BankCSVTransaction, on_delete=models.CASCADE,
        related_name='original_transaction_reimbursed'
    )
    reimbursement_from_vena = models.ForeignKey(
        BankCSVTransaction, on_delete=models.CASCADE,
        related_name='reimbursement_from_vena_for'
    )


class LegacyTransactionDetailsCSVTransaction(TransactionBase):
    category = models.CharField(
        max_length=300
    )

    def __str__(self):
        return f"LegacyTransaction date [{self.get_date}] payment method [{self.payment_method}] target [{self.purchase_target}] type [{self.type}] name [{self.name}] memo [{self.memo}] price [{self.price}] store [{self.store}] category [{self.category}]"


class TransactionLabel(models.Model):
    label = models.CharField(
        max_length=300
    )


class TransactionLabelIntersection(models.Model):
    transaction = models.ForeignKey(BankCSVTransaction, on_delete=models.CASCADE)
    label = models.ForeignKey(TransactionLabel, on_delete=models.CASCADE)


class Item(models.Model):
    name = models.CharField(
        max_length=300
    )
    price = models.FloatField(

    )
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
    purchased_by_choices = (
        ('Me', 'Me'),
        ('Vena', 'Vena'),
    )
    purchased_by = models.CharField(
        max_length=50,
        choices=purchased_by_choices,
        default="Me"
    )
    category = models.ForeignKey(
        TransactionCategory, on_delete=models.CASCADE, null=True
    )
    note = models.CharField(
        max_length=300
    )
    transaction = models.ForeignKey(BankCSVTransaction, on_delete=models.CASCADE)


class ItemLabel(models.Model):
    label = models.CharField(
        max_length=300
    )
    transaction = models.ForeignKey(Item, on_delete=models.CASCADE)


class ItemLabelIntersection(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    label = models.ForeignKey(ItemLabel, on_delete=models.CASCADE)
