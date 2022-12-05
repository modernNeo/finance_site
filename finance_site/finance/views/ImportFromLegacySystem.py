import csv
import datetime

import pytz
from django.http import HttpResponseRedirect
from django.views.generic.base import View

from finance_site.settings import BASE_DIR
from finance.models.GroupingModels import ItemLabelIntersection, ItemReimbursement, TransactionRefund, \
    ETransferToInternalTransferMapping, TransactionReimbursement, ItemPayBack
from finance.models.ItemModels import ItemLabel, Item
from finance.models.TransactionModels import TransactionCategory, TransactionLabelIntersection, Transaction, \
    LegacyTransaction, TransactionBase, TransactionLabel


class ImportFromLegacySystem(View):
    def get(self, request):
        ItemLabelIntersection.objects.all().delete()
        ItemLabel.objects.all().delete()
        ItemReimbursement.objects.all().delete()
        Item.objects.all().delete()

        TransactionCategory.objects.all().delete()
        TransactionCategory.objects.bulk_create([
            TransactionCategory(category="Income"),
            TransactionCategory(category="Government Deposit"),
            TransactionCategory(category="Numeris"),
            TransactionCategory(category="Misc Income"),

            TransactionCategory(category="Charity Donation"),
            TransactionCategory(category="Household Necessity"),
            TransactionCategory(category="Chomp"),
            TransactionCategory(category="Leisure"),
            TransactionCategory(category="Online Purchase"),
            TransactionCategory(category="Theatres/New DVD releases"),
            TransactionCategory(category="Music/Movies"),
            TransactionCategory(category="Pho Friday"),
            TransactionCategory(category="Recurring Monthly Bill"),
            TransactionCategory(category="Rent"),
            TransactionCategory(category="Spanish Tutoring"),
            TransactionCategory(category="Yearly Subscription"),
            TransactionCategory(category="Student Loans"),
            TransactionCategory(category="Automated Student Loans Payment"),
            TransactionCategory(category="Regular Withdrawals"),
            TransactionCategory(category="Home-Office"),
            TransactionCategory(category="Couple's Counselling"),
            TransactionCategory(category="Medical"),
            TransactionCategory(category="Beauty/Vanity"),

            TransactionCategory(category="Homeless People"),

            TransactionCategory(category="Mastercard Payment"),
            TransactionCategory(category="Mastercard Payment For Dawn"), #payments I made to my mastercard for shit I bought for Dawn

            TransactionCategory(category="Medical Reimbursement"),
            TransactionCategory(category="Vena Perks Reimbursement"),
            TransactionCategory(category="Temporary Vena Peks Reimbursement"),
            TransactionCategory(category="Dawn Payment for Prime"),
            TransactionCategory(category="Dawn Payment for Spanish Tutoring"),
            TransactionCategory(category="Dawn Payment for Leisures"),
            TransactionCategory(category="Dawn Payment for Counselling"),

            TransactionCategory(category="Not My Expense"),
            TransactionCategory(category="Misc Reimbursement"),
            TransactionCategory(category="Partial"),
            TransactionCategory(category="Categorized Elsewhere")
        ])
        TransactionRefund.objects.all().delete()
        ETransferToInternalTransferMapping.objects.all().delete()
        TransactionReimbursement.objects.all().delete()
        TransactionLabelIntersection.objects.all().delete()

        Transaction.objects.all().delete()
        LegacyTransaction.objects.all().delete()
        TransactionBase.objects.all().delete()

        TransactionLabel.objects.all().delete()
        with open(f"{BASE_DIR.parent}/chequing.csv", 'r') as credit_card:
            csvFile = csv.reader(credit_card)
            for line in csvFile:
                date = None
                try:
                    date = datetime.datetime.strptime(line[0], "%m/%d/%Y").astimezone(
                        pytz.timezone('America/Vancouver')
                    )
                except ValueError:
                    pass
                if date is not None:
                    Transaction(
                        month=date,
                        date=date,
                        payment_method="Debit Card",
                        method_of_transaction=line[1],
                        name=line[2],
                        memo=line[3],
                        price=line[4]
                    ).save()
        with open(f"{BASE_DIR.parent}/credit_card.csv", 'r') as credit_card:
            csvFile = csv.reader(credit_card)
            for line in csvFile:
                date = None
                try:
                    date = datetime.datetime.strptime(line[0], "%m/%d/%Y").astimezone(
                        pytz.timezone('America/Vancouver')
                    )
                except ValueError:
                    pass
                if date is not None:
                    Transaction(
                        month=date,
                        date=date,
                        payment_method="Mastercard",
                        method_of_transaction=line[1],
                        name=line[2],
                        memo=line[3],
                        price=line[4]
                    ).save()
        with open(f"{BASE_DIR.parent}/transaction_details_v2.csv", 'r') as transaction_details:
            csvFile = csv.reader(transaction_details)
            i = 0
            csvFile = list(reversed([line for line in csvFile]))
            ticket_bought_for_mirch = None
            ticket_bought_for_dawn = None
            categorized_transactions = []
            while i < len(csvFile):
                legacy_transaction_detail = csvFile[i]
                if legacy_transaction_detail[2].lower() == "MASTERCARD".lower():
                    date = None
                    try:
                        date = datetime.datetime.strptime(legacy_transaction_detail[1], "%Y-%m-%d").astimezone(
                            pytz.timezone('America/Vancouver')
                        )
                    except ValueError:
                        pass
                    if date is not None:
                        month = f"{legacy_transaction_detail[0]}-01"
                        payment_method = legacy_transaction_detail[2]
                        method_of_transaction = legacy_transaction_detail[3]
                        name = legacy_transaction_detail[4]
                        memo = legacy_transaction_detail[5]
                        price = float(legacy_transaction_detail[6].replace("$", "").replace(",", ""))
                        category_str = legacy_transaction_detail[7]
                        note = legacy_transaction_detail[8]
                        matching_uncategorized_bank_csv_transactions = Transaction.get_uncategorized_with_memo(
                            date,
                            method_of_transaction,
                            name,
                            memo,
                            price)
                        categories = TransactionCategory.objects.all().filter(category=category_str)
                        if len(matching_uncategorized_bank_csv_transactions) == 0:
                            LegacyTransaction(
                                month=month,
                                date=date,
                                payment_method=payment_method,
                                method_of_transaction=method_of_transaction,
                                name=name,
                                memo=memo,
                                price=price,
                                category=category_str,
                                note=note
                            ).save()
                        else:
                            matching_uncategorized_bank_csv_transaction = matching_uncategorized_bank_csv_transactions[
                                0]
                            if "paypal *cineplex" in name.lower() and len(categories) != 1:
                                if "refund" in category_str.lower():
                                    original_transaction = \
                                        Transaction.objects.filter(name=name, price=price - (2 * price))[0]
                                    TransactionRefund(
                                        original_transaction=original_transaction,
                                        refund_transaction=matching_uncategorized_bank_csv_transaction
                                    ).save()
                                    if original_transaction.category is None:
                                        raise Exception("something no good....")
                                    matching_uncategorized_bank_csv_transaction.category = original_transaction.category
                                    matching_uncategorized_bank_csv_transaction.note = note
                                    matching_uncategorized_bank_csv_transaction.month = month
                                    matching_uncategorized_bank_csv_transaction.purchase_target = original_transaction.purchase_target
                                    matching_uncategorized_bank_csv_transaction.who_will_pay = original_transaction.who_will_pay
                                    matching_uncategorized_bank_csv_transaction.save()
                                    categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                                else:
                                    item_saved = False
                                    item_name = f"{name} | {category_str}"
                                    category_str = "Theatres/New DVD releases"
                                    last_item = i - 1
                                    while (csvFile[last_item - 1][1]) == "":
                                        last_item -= 1
                                    while last_item != i:
                                        legacy_transaction_detail_item = csvFile[last_item]
                                        price = float(legacy_transaction_detail_item[6].replace("$", ""))
                                        purchase_target = legacy_transaction_detail_item[7]
                                        note = legacy_transaction_detail_item[8]
                                        if "dawn" in purchase_target.lower():
                                            purchase_target = "Dawn"
                                        elif "mir" in purchase_target.lower():
                                            purchase_target = "Mircea"
                                        elif purchase_target.lower() == category_str.lower():
                                            purchase_target = "Me"
                                        else:
                                            raise Exception(
                                                f"Unable to determine purchase target for item [{item_name}] in transaction "
                                                f"[{matching_uncategorized_bank_csv_transaction}]"
                                            )
                                        category = TransactionCategory.objects.all().get(category=category_str) \
                                            if purchase_target == "Me" else TransactionCategory.objects.all().get(
                                            category="Not My Expense")
                                        item = Item(
                                            name=item_name,
                                            price=price,
                                            purchase_target=purchase_target,
                                            who_will_pay=purchase_target,
                                            category=category,
                                            transaction=matching_uncategorized_bank_csv_transaction,
                                            note=note
                                        )
                                        item.save()
                                        matching_uncategorized_bank_csv_transaction.processed = True
                                        if purchase_target == "Mircea":
                                            ticket_bought_for_mirch = item
                                        if purchase_target == "Dawn":
                                            ticket_bought_for_dawn = item
                                        item_saved = True
                                        last_item += 1
                                    if not item_saved:
                                        raise Exception(
                                            f"Unable to properly save item [{item_name}] in transaction "
                                            f"[{matching_uncategorized_bank_csv_transaction}]"
                                        )
                                    matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                        category="Partial")
                                    matching_uncategorized_bank_csv_transaction.month = month
                                    matching_uncategorized_bank_csv_transaction.purchase_target = "Group Purchase"
                                    matching_uncategorized_bank_csv_transaction.who_will_pay = "Group Purchase"
                                    matching_uncategorized_bank_csv_transaction.save()
                                    categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            elif "Total Payment for Spanish Lesson".lower() == category_str.lower() or "Total Payment for Spanish books".lower() == category_str.lower():
                                item_saved = False
                                item_name = f"{name} | {category_str}"
                                category_str = "Spanish Tutoring"
                                last_item = i - 1
                                while (csvFile[last_item - 1][1]) == "":
                                    last_item -= 1
                                while last_item != i:
                                    legacy_transaction_detail_item = csvFile[last_item]
                                    price = float(legacy_transaction_detail_item[6].replace("$", ""))
                                    purchase_target = legacy_transaction_detail_item[7]
                                    note = legacy_transaction_detail_item[8]
                                    if "dawn" in purchase_target.lower():
                                        purchase_target = "Dawn"
                                    elif purchase_target.lower() == category_str.lower():
                                        purchase_target = "Me"
                                    else:
                                        raise Exception(
                                            f"Unable to determine purchase target for item [{item_name}] in transaction "
                                            f"[{matching_uncategorized_bank_csv_transaction}]"
                                        )
                                    category = TransactionCategory.objects.all().get(category=category_str) \
                                        if purchase_target == "Me" else TransactionCategory.objects.all().get(
                                        category="Not My Expense")
                                    item = Item(
                                        name=item_name,
                                        price=price,
                                        purchase_target=purchase_target,
                                        who_will_pay=purchase_target,
                                        category=category,
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                        note=note
                                    )
                                    item.save()
                                    matching_uncategorized_bank_csv_transaction.processed = True
                                    item_saved = True
                                    last_item += 1
                                if not item_saved:
                                    raise Exception(
                                        f"Unable to properly save item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                                matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                    category="Partial")
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.purchase_target = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.who_will_pay = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            elif "Total Payment for Leisure".lower() == category_str.lower():
                                item_saved = False
                                item_name = f"{name} | {category_str}"
                                category_str = "Leisure"
                                last_item = i - 1
                                while (csvFile[last_item - 1][1]) == "":
                                    last_item -= 1
                                while last_item != i:
                                    legacy_transaction_detail_item = csvFile[last_item]
                                    price = float(legacy_transaction_detail_item[6].replace("$", ""))
                                    purchase_target = legacy_transaction_detail_item[7]
                                    note = legacy_transaction_detail_item[8]
                                    if "dawn" in purchase_target.lower():
                                        purchase_target = "Dawn"
                                    elif purchase_target.lower() == category_str.lower():
                                        purchase_target = "Me"
                                    else:
                                        raise Exception(
                                            f"Unable to determine purchase target for item [{item_name}] in transaction "
                                            f"[{matching_uncategorized_bank_csv_transaction}]"
                                        )
                                    category = TransactionCategory.objects.all().get(category=category_str) \
                                        if purchase_target == "Me" else TransactionCategory.objects.all().get(
                                        category="Not My Expense")
                                    item = Item(
                                        name=item_name,
                                        price=price,
                                        purchase_target=purchase_target,
                                        who_will_pay=purchase_target,
                                        category=category,
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                        note=note
                                    )
                                    item.save()
                                    matching_uncategorized_bank_csv_transaction.processed = True
                                    item_saved = True
                                    last_item += 1
                                if not item_saved:
                                    raise Exception(
                                        f"Unable to properly save item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                                matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                    category="Partial")
                                matching_uncategorized_bank_csv_transaction.purchase_target = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.who_will_pay = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            elif "Total Payment for Couple's Counselling".lower() == category_str.lower():
                                item_saved = False
                                item_name = f"{name} | {category_str}"
                                category_str = "Medical"
                                last_item = i - 1
                                while (csvFile[last_item - 1][1]) == "":
                                    last_item -= 1
                                while last_item != i:
                                    legacy_transaction_detail_item = csvFile[last_item]
                                    price = float(legacy_transaction_detail_item[6].replace("$", ""))
                                    purchase_target = legacy_transaction_detail_item[7]
                                    note = legacy_transaction_detail_item[8]
                                    if "dawn" in purchase_target.lower():
                                        purchase_target = "Dawn"
                                    elif purchase_target.lower() == category_str.lower():
                                        purchase_target = "Me"
                                    else:
                                        raise Exception(
                                            f"Unable to determine purchase target for item [{item_name}] in transaction "
                                            f"[{matching_uncategorized_bank_csv_transaction}]"
                                        )
                                    category = TransactionCategory.objects.all().get(category=category_str) \
                                        if purchase_target == "Me" else TransactionCategory.objects.all().get(
                                        category="Not My Expense")
                                    item = Item(
                                        name=item_name,
                                        price=price,
                                        purchase_target=purchase_target,
                                        who_will_pay=purchase_target,
                                        category=category,
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                        note=note
                                    )
                                    item.save()
                                    matching_uncategorized_bank_csv_transaction.processed = True
                                    item_saved = True
                                    last_item += 1
                                if not item_saved:
                                    raise Exception(
                                        f"Unable to properly save item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                                matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                    category="Partial")
                                matching_uncategorized_bank_csv_transaction.purchase_target = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.who_will_pay = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            elif "Team Lunch".lower() in category_str.lower():
                                # need to add logic for processing DEBIT deposits for reimbursements
                                item_saved = False
                                item_name = f"{name} | {category_str}"
                                category_str = "Leisure"
                                last_item = i - 1
                                while (csvFile[last_item - 1][1]) == "":
                                    last_item -= 1
                                while last_item != i:
                                    legacy_transaction_detail_item = csvFile[last_item]
                                    price = float(legacy_transaction_detail_item[6].replace("$", ""))
                                    who_will_pay = legacy_transaction_detail_item[7]
                                    note = legacy_transaction_detail_item[8]
                                    if "vena" in who_will_pay.lower():
                                        who_will_pay = "Vena"
                                    elif who_will_pay.lower() == category_str.lower():
                                        who_will_pay = "Me"
                                    elif "dawn" in who_will_pay.lower():
                                        who_will_pay = "Dawn"
                                    else:
                                        raise Exception(
                                            f"Unable to determine purchase target for item [{item_name}] in transaction "
                                            f"[{matching_uncategorized_bank_csv_transaction}]"
                                        )
                                    category = TransactionCategory.objects.all().get(category=category_str) \
                                        if who_will_pay == "Me" else TransactionCategory.objects.all().get(
                                        category="Not My Expense")
                                    purchase_target = "Me" if who_will_pay != "Dawn" else who_will_pay
                                    item = Item(
                                        name=item_name,
                                        price=price,
                                        who_will_pay=who_will_pay,
                                        purchase_target=purchase_target,
                                        category=category,
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                        note=note
                                    )
                                    item.save()
                                    matching_uncategorized_bank_csv_transaction.processed = True
                                    item_saved = True
                                    last_item += 1
                                if not item_saved:
                                    raise Exception(
                                        f"Unable to properly save item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                                matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                    category="Partial")
                                matching_uncategorized_bank_csv_transaction.purchase_target = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.who_will_pay = "Group Purchase"
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            elif "Refund".lower() in category_str.lower():
                                original_transactions = \
                                    Transaction.objects.filter(
                                        name=name, price=price - (2 * price),
                                    )
                                original_tran = None
                                for original_transaction in original_transactions:
                                    if len(original_transaction.reimbursements_mapping_set.all()) == 0:
                                        original_tran = original_transaction
                                if original_tran is None:
                                    raise Exception("Could not find the original transaction to refund")
                                TransactionRefund(
                                    original_transaction=original_tran,
                                    refund_transaction=matching_uncategorized_bank_csv_transaction
                                ).save()
                                matching_uncategorized_bank_csv_transaction.category = original_transaction.category
                                matching_uncategorized_bank_csv_transaction.purchase_target = original_transaction.purchase_target
                                matching_uncategorized_bank_csv_transaction.who_will_pay = original_transaction.who_will_pay
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                            else:
                                if name.lower() == "PAYMENT - THANK YOU".lower():
                                    category_str = "Mastercard Payment"
                                    categories = TransactionCategory.objects.all().filter(category=category_str)
                                elif category_str.lower() == "Combined Amazon Purchase".lower():
                                    category_str = "Categorized Elsewhere"
                                    categories = TransactionCategory.objects.all().filter(category=category_str)
                                    home_office_item = csvFile[i - 1]
                                    online_purchase = csvFile[i - 2]
                                    Item(
                                        name=matching_uncategorized_bank_csv_transaction.name,
                                        price=float(home_office_item[6].replace("$", "")),
                                        who_will_pay="Me",
                                        purchase_target="Me",
                                        category=TransactionCategory.objects.all().filter(category=home_office_item[7])[0],
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                    ).save()
                                    Item(
                                        name=matching_uncategorized_bank_csv_transaction.name,
                                        price=float(online_purchase[6].replace("$", "")),
                                        who_will_pay="Me",
                                        purchase_target="Me",
                                        category=TransactionCategory.objects.all().filter(category=online_purchase[7])[0],
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                    ).save()
                                elif category_str.lower() == "Not My Expense".lower():
                                    categories = TransactionCategory.objects.all().filter(category=category_str)
                                    if note.lower() == "Dawn paid for item for me".lower():
                                        matching_uncategorized_bank_csv_transaction.who_will_pay = 'Dawn'
                                    elif note.lower() == "bought something for Dawn and she paid back".lower():
                                        matching_uncategorized_bank_csv_transaction.purchase_target = "Dawn"
                                        matching_uncategorized_bank_csv_transaction.who_will_pay = "Dawn"
                                    elif note.lower() == "Dawn’s session with Melanie that got charged to me [paid on 2022-10-02]".lower():
                                        matching_uncategorized_bank_csv_transaction.purchase_target = 'Dawn'
                                        matching_uncategorized_bank_csv_transaction.who_will_pay = 'Dawn'
                                    elif "michael" in note.lower():
                                        matching_uncategorized_bank_csv_transaction.who_will_pay = 'Micheal'
                                    elif 'dawn' in note.lower():
                                        matching_uncategorized_bank_csv_transaction.purchase_target = 'Dawn'
                                        matching_uncategorized_bank_csv_transaction.who_will_pay = 'Dawn'
                                    matching_uncategorized_bank_csv_transaction.save()
                                if len(categories) == 0:
                                    print(legacy_transaction_detail)
                                    raise Exception(f"Invalid category of [{category_str}] detected in [{date}]")
                                else:
                                    category = categories[0]
                                matching_uncategorized_bank_csv_transaction.category = category
                                matching_uncategorized_bank_csv_transaction.note = note
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                matching_uncategorized_bank_csv_transaction.processed = True
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                elif legacy_transaction_detail[2].lower() == "DEBIT".lower():
                    date = None
                    try:
                        date = datetime.datetime.strptime(legacy_transaction_detail[1], "%Y-%m-%d").astimezone(
                            pytz.timezone('America/Vancouver')
                        )
                    except ValueError:
                        pass
                    if date is not None:
                        month = f"{legacy_transaction_detail[0]}-01"
                        payment_method = "Debit Card"
                        method_of_transaction = legacy_transaction_detail[3]
                        name = legacy_transaction_detail[4]
                        memo = legacy_transaction_detail[5]
                        price = float(legacy_transaction_detail[6].replace("$", "").replace(",", ""))
                        category_str = legacy_transaction_detail[7]
                        note = legacy_transaction_detail[8]
                        matching_uncategorized_bank_csv_transactions = Transaction.get_uncategorized_with_memo(
                            date,
                            method_of_transaction,
                            name,
                            memo,
                            price)
                        if len(matching_uncategorized_bank_csv_transactions) == 0:
                            matching_uncategorized_bank_csv_transactions = Transaction.get_uncategorized_with_memo(
                                date,
                                method_of_transaction,
                                name,
                                memo,
                                abs(price))
                        if category_str in ["Dawn reimbursement", "Mirchero reimbursement"]:
                            if len(matching_uncategorized_bank_csv_transactions) == 0:
                                LegacyTransaction(
                                    month=month,
                                    date=date,
                                    payment_method=payment_method,
                                    method_of_transaction=method_of_transaction,
                                    name=name,
                                    memo=memo,
                                    price=price,
                                    category=category_str,
                                    note=note
                                ).save()
                            else:
                                matching_uncategorized_bank_csv_transaction = matching_uncategorized_bank_csv_transactions[0]
                                if category_str == "Dawn reimbursement":
                                    ticket = ticket_bought_for_dawn
                                    ticket_bought_for_dawn = None
                                    if abs(price) != abs(ticket.price):
                                        raise Exception(f"dawn reimbursement is {price} but ticket was {ticket.price}")
                                else:
                                    ticket = ticket_bought_for_mirch
                                    ticket_bought_for_mirch = None
                                    if abs(price) != abs(ticket.price):
                                        raise Exception(
                                            f"mirchea reimbursement is {price} but ticket was {ticket.price}")
                                ItemPayBack(
                                    original_item=ticket,
                                    payback_transaction = matching_uncategorized_bank_csv_transaction,
                                    note=ticket.category
                                ).save()
                                matching_uncategorized_bank_csv_transaction.category = ticket.category
                                del ticket
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                        elif "transfer_below-" in category_str:
                            matching_uncategorized_bank_csv_transaction = matching_uncategorized_bank_csv_transactions[
                                0]
                            last_x_trans_length = int(category_str.split("-")[1])
                            relevant_transactions = categorized_transactions[-last_x_trans_length:]
                            for relevant_transaction in relevant_transactions:
                                ETransferToInternalTransferMapping(
                                    e_transfer=matching_uncategorized_bank_csv_transaction,
                                    internal_transfer=relevant_transaction
                                ).save()
                            matching_uncategorized_bank_csv_transaction.category = TransactionCategory.objects.all().get(
                                category="Categorized Elsewhere")
                            matching_uncategorized_bank_csv_transaction.month = month
                            matching_uncategorized_bank_csv_transaction.save()
                            categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                        else:
                            categories = TransactionCategory.objects.all().filter(category=category_str)
                            if len(matching_uncategorized_bank_csv_transactions) == 0:
                                LegacyTransaction(
                                    month=month,
                                    date=date,
                                    payment_method=payment_method,
                                    method_of_transaction=method_of_transaction,
                                    name=name,
                                    memo=memo,
                                    price=price,
                                    category=category_str,
                                    note=note
                                ).save()
                            else:
                                matching_uncategorized_bank_csv_transaction = \
                                matching_uncategorized_bank_csv_transactions[0]
                                if len(categories) == 0:
                                    print(legacy_transaction_detail)
                                    raise Exception(f"Invalid category of [{category_str}] detected in [{date}]")
                                else:
                                    category = categories[0]
                                matching_uncategorized_bank_csv_transaction.category = category
                                matching_uncategorized_bank_csv_transaction.month = month
                                matching_uncategorized_bank_csv_transaction.note = note
                                matching_uncategorized_bank_csv_transaction.save()
                                categorized_transactions.append(matching_uncategorized_bank_csv_transaction)
                i += 1
        return HttpResponseRedirect("/")

