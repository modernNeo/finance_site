import csv
import datetime

import pytz
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View
from querystring_parser import parser
# Create your views here.
from finance_site.models import BankCSVTransaction, TransactionCategory, LegacyTransactionDetailsCSVTransaction, Item, \
    ReceiptRefund


class ShowCategorizedTransactions(View):
    def get(self, request):
        transactions = BankCSVTransaction.objects.all().order_by('-date')
        categorized_transactions = []
        for transaction in transactions:
            if transaction.category is not None or len(transaction.item_set.all()) > 0:
                categorized_transactions.append(transaction)
                if transaction.category is None:
                    for item in transaction.item_set.all():
                        categorized_transactions.append(item)
            refunds_receipt = transaction.get_refund_receipts()
            if len(refunds_receipt) > 0:
                categorized_transactions.append({
                    "name": "REFUNDED-BY"
                })
            categorized_transactions.extend(refunds_receipt)
            original_receipts = transaction.get_original_receipts()
            if len(original_receipts) > 0:
                categorized_transactions.append({
                    "name": "ORIGINAL-RECEIPT-BEING-REFUNDED"
                })
            categorized_transactions.extend(original_receipts)
        return render(
            request, 'index.html', context=
            {
                "transactions": categorized_transactions,
                "current_page": "home"
            }
        )


class ShowUncategorizedTransactions(View):
    def get(self, request):
        transactions = BankCSVTransaction.objects.all().filter(
            date__lte=datetime.datetime.strptime("2022-11-02", "%Y-%m-%d")).order_by('-date')
        uncategorized_transactions = []
        for transaction in transactions:
            if transaction.category is None and len(transaction.item_set.all()) == 0:
                uncategorized_transactions.append(transaction)

        return render(
            request, 'uncategorized_transactions.html', context=
            {
                "transactions": uncategorized_transactions,
                "current_page": "uncategorized_transactions"
            }
        )


def add_transaction_view(request):
    return render(request, 'add_transaction.html')


class LinkUnlinkedLegacyTransactionDetailsCSVTransactions(View):
    def get(self, request):
        request_path = request.path

        current_page = request.GET.get('p', 'none')
        if current_page == 'none':
            current_page = 1
        else:
            current_page = int(current_page)
        unlinked_bank_csv_transactions = BankCSVTransaction.objects.all().filter(category__isnull=True)
        paginated_object = Paginator(LegacyTransactionDetailsCSVTransaction.objects.all().order_by('-date'),
                                     per_page=30)
        if paginated_object.num_pages < current_page:
            return HttpResponseRedirect(request_path)

        legacy_transaction_details_csv_transactions = paginated_object.page(current_page)

        previous_button_link = request_path + '?p=' + str(
            current_page - 1 if current_page > 1 else paginated_object.num_pages
        )
        next_button_link = request_path + '?p=' + str(
            current_page + 1 if current_page + 1 <= paginated_object.num_pages else 1
        )
        return render(
            request, 'unfinalized_transactions.html',
            context={
                "legacy_transaction_details_csv_transactions": legacy_transaction_details_csv_transactions,
                "unlinked_transactions": unlinked_bank_csv_transactions,
                "current_page": "unfinalized_legacy_transactions",
                'nextButtonLink': next_button_link,
                'previousButtonLink': previous_button_link,

            }
        )

    def post(self, request):
        unfinalized_legacy_transactions = list(
            (parser.parse(request.POST.urlencode()))['legacy_transaction_details_csv_transactions'].values()
        )
        unfinalized_legacy_transactions = [
            unfinalized_legacy_transaction
            for unfinalized_legacy_transaction in unfinalized_legacy_transactions
            if unfinalized_legacy_transaction["bank_transaction"] != "None"
        ]
        unlinked_bank_csv_transactions = BankCSVTransaction.objects.all().filter(category__isnull=True)
        for unfinalized_legacy_transaction in unfinalized_legacy_transactions:
            # {'id': '1275', 'payment_method': 'MASTERCARD', 'name': 'DONALDS MARKET VANCOUVER BC',
            #  'memo': 'Rewards earned: 2.20 ~ Category: Groceries', 'store': '', 'category': 'Household Necessity'}
            print(unfinalized_legacy_transaction)
            matching_bank_csv_transaction = unlinked_bank_csv_transactions.get(
                id=int(unfinalized_legacy_transaction['bank_transaction'])
            )
            matching_bank_csv_transaction.category = TransactionCategory.objects.get(
                category=unfinalized_legacy_transaction['category']
            )
            matching_bank_csv_transaction.save()
            LegacyTransactionDetailsCSVTransaction.objects.get(id=int(unfinalized_legacy_transaction['id'])).delete()
        legacy_transaction_details_csv_transactions = LegacyTransactionDetailsCSVTransaction.objects.all()
        return render(
            request, 'unfinalized_transactions.html',
            context={
                "legacy_transaction_details_csv_transactions": legacy_transaction_details_csv_transactions,
                "unlinked_transactions": unlinked_bank_csv_transactions,
                "current_page": "unfinalized_legacy_transactions"
            }
        )


class ImportFromLegacySystem(View):
    def get(self, request):
        BankCSVTransaction.objects.all().delete()
        TransactionCategory.objects.all().delete()
        TransactionCategory.objects.bulk_create([
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

            TransactionCategory(category="Home-Office"),

            TransactionCategory(category="Couple's Counselling"),
            TransactionCategory(category="Medical"),

            TransactionCategory(category="Homeless People"),
            TransactionCategory(category="Beauty/Vanity"),

            TransactionCategory(category="Income"),
            TransactionCategory(category="Medical Reimbursement"),
            TransactionCategory(category="Misc Income"),
            TransactionCategory(category="Numeris"),
            TransactionCategory(category="Government Deposit"),

            TransactionCategory(category="Mastercard Payment"),

            TransactionCategory(category="Error Charge"),
            TransactionCategory(category="For Dawn"),

            TransactionCategory(category="Not My Expense")
        ])
        LegacyTransactionDetailsCSVTransaction.objects.all().delete()
        with open("/media/jace/jace_docs/2_personal/finance/credit_card.csv", 'r') as credit_card:
            csvFile = csv.reader(credit_card)
            for line in csvFile:
                date = None
                try:
                    date = datetime.datetime.strptime(line[0], "%m/%d/%Y").astimezone(
                        pytz.timezone('America/Vancouver')
                    ) + datetime.timedelta(hours=8)
                except ValueError:
                    pass
                if date is not None:
                    BankCSVTransaction(
                        month=date,
                        date=date,
                        payment_method="Mastercard",
                        method_of_transaction=line[1],
                        name=line[2],
                        memo=line[3],
                        price=line[4]
                    ).save()
        with open("/media/jace/jace_docs/2_personal/finance/transaction_details.csv", 'r') as transaction_details:
            csvFile = csv.reader(transaction_details)
            i = 0
            csvFile = list(reversed([line for line in csvFile]))
            while i < len(csvFile):
                legacy_transaction_detail = csvFile[i]
                if legacy_transaction_detail[2].lower() != "MASTERCARD".lower():
                    # print(f"{i}-skipping a non mastercard transaction")
                    i += 1
                    continue
                date = None
                try:
                    date = datetime.datetime.strptime(legacy_transaction_detail[1], "%Y-%m-%d").astimezone(
                        pytz.timezone('America/Vancouver')
                    ) + datetime.timedelta(hours=8)
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
                    matching_uncategorized_bank_csv_transactions = BankCSVTransaction.get_uncategorized_with_memo(date,
                                                                                                                  method_of_transaction,
                                                                                                                  name,
                                                                                                                  memo,
                                                                                                                  price)
                    categories = TransactionCategory.objects.all().filter(category=category_str)
                    if len(matching_uncategorized_bank_csv_transactions) == 0:
                        LegacyTransactionDetailsCSVTransaction(
                            month=month,
                            date=date,
                            payment_method=payment_method,
                            method_of_transaction=method_of_transaction,
                            name=name,
                            memo=memo,
                            price=price,
                            category=category_str
                        ).save()
                    else:
                        matching_uncategorized_bank_csv_transaction = matching_uncategorized_bank_csv_transactions[0]
                        if "paypal *cineplex" in name.lower() and len(categories) != 1:
                            if "refund" in category_str.lower():
                                print(f"cineplex refund detected for {category_str} on {date}")
                                print(legacy_transaction_detail)
                                original_transaction = \
                                BankCSVTransaction.objects.filter(name=name, price=price - (2 * price))[0]
                                ReceiptRefund(
                                    original_transaction_in_refund=original_transaction,
                                    refund_transaction_in_refund=matching_uncategorized_bank_csv_transaction
                                ).save()
                                item_name = f"{name} | {category_str}"
                                if original_transaction.category is None and len(
                                    original_transaction.item_set.all()) > 0:
                                    for original_item in original_transaction.item_set.all():
                                        Item(
                                            name=item_name,
                                            price=original_item.price - (2 * original_item.price),
                                            purchase_target=original_item.purchase_target,
                                            waiting_for_reimbursement=original_item.waiting_for_reimbursement,
                                            purchased_by=original_item.purchased_by,
                                            category=original_item.category,
                                            transaction=matching_uncategorized_bank_csv_transaction,
                                            note=note
                                        ).save()
                                elif original_transaction.category is not None:
                                    matching_uncategorized_bank_csv_transaction.category = original_transaction.category
                                    matching_uncategorized_bank_csv_transaction.note = note
                                    matching_uncategorized_bank_csv_transaction.save()
                                else:
                                    raise Exception("Could not detect category on original cineplex receipt")
                            else:
                                item_saved = False
                                item_name = f"{name} | {category_str}"
                                category_str = "Theatres/New DVD releases"
                                last_item = i - 1
                                while (csvFile[last_item - 1][1]) == "":
                                    last_item -= 1
                                while last_item != i:
                                    legacy_transaction_detail_item = csvFile[last_item]
                                    price = legacy_transaction_detail_item[6]
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
                                        if purchase_target == "Me" else None
                                    Item(
                                        name=item_name,
                                        price=price.replace("$", ""),
                                        purchase_target=purchase_target,
                                        purchased_by=purchase_target,
                                        category=category,
                                        transaction=matching_uncategorized_bank_csv_transaction,
                                        note=note
                                    ).save()
                                    item_saved = True
                                    last_item += 1
                                if not item_saved:
                                    raise Exception(
                                        f"Unable to properly save item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                        elif "Total Payment for Spanish Lesson".lower() == category_str.lower() or "Total Payment for Spanish books".lower() == category_str.lower():
                            item_saved = False
                            item_name = f"{name} | {category_str}"
                            category_str = "Spanish Tutoring"
                            last_item = i - 1
                            while (csvFile[last_item - 1][1]) == "":
                                last_item -= 1
                            while last_item != i:
                                legacy_transaction_detail_item = csvFile[last_item]
                                price = legacy_transaction_detail_item[6]
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
                                    if purchase_target == "Me" else None
                                Item(
                                    name=item_name,
                                    price=price.replace("$", ""),
                                    purchase_target=purchase_target,
                                    purchased_by=purchase_target,
                                    category=category,
                                    transaction=matching_uncategorized_bank_csv_transaction,
                                    note=note
                                ).save()
                                item_saved = True
                                last_item += 1
                            if not item_saved:
                                raise Exception(
                                    f"Unable to properly save item [{item_name}] in transaction "
                                    f"[{matching_uncategorized_bank_csv_transaction}]"
                                )
                        elif "Total Payment for Leisure".lower() == category_str.lower():
                            item_saved = False
                            item_name = f"{name} | {category}"
                            category_str = "Leisure"
                            last_item = i - 1
                            while (csvFile[last_item - 1][1]) == "":
                                last_item -= 1
                            while last_item != i:
                                legacy_transaction_detail_item = csvFile[last_item]
                                price = legacy_transaction_detail_item[6]
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
                                    if purchase_target == "Me" else None
                                Item(
                                    name=item_name,
                                    price=price.replace("$", ""),
                                    purchase_target=purchase_target,
                                    purchased_by=purchase_target,
                                    category=category,
                                    transaction=matching_uncategorized_bank_csv_transaction,
                                    note=note
                                ).save()
                                item_saved = True
                                last_item += 1
                            if not item_saved:
                                raise Exception(
                                    f"Unable to properly save item [{item_name}] in transaction "
                                    f"[{matching_uncategorized_bank_csv_transaction}]"
                                )
                        elif "Total Payment for Couple's Counselling".lower() == category_str.lower():
                            item_saved = False
                            item_name = f"{name} | {category}"
                            category_str = "Medical"
                            last_item = i - 1
                            while (csvFile[last_item - 1][1]) == "":
                                last_item -= 1
                            while last_item != i:
                                legacy_transaction_detail_item = csvFile[last_item]
                                price = legacy_transaction_detail_item[6]
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
                                    if purchase_target == "Me" else None
                                Item(
                                    name=item_name,
                                    price=price.replace("$", ""),
                                    purchase_target=purchase_target,
                                    purchased_by=purchase_target,
                                    category=category,
                                    transaction=matching_uncategorized_bank_csv_transaction,
                                    note=note
                                ).save()
                                item_saved = True
                                last_item += 1
                            if not item_saved:
                                raise Exception(
                                    f"Unable to properly save item [{item_name}] in transaction "
                                    f"[{matching_uncategorized_bank_csv_transaction}]"
                                )
                        elif "Team Lunch".lower() in category_str.lower():
                            # need to add logic for processing DEBIT deposits for reimbursements
                            item_saved = False
                            item_name = f"{name} | {category}"
                            category_str = "Leisure"
                            last_item = i - 1
                            while (csvFile[last_item - 1][1]) == "":
                                last_item -= 1
                            while last_item != i:
                                legacy_transaction_detail_item = csvFile[last_item]
                                price = legacy_transaction_detail_item[6]
                                purchased_by = legacy_transaction_detail_item[7]
                                note = legacy_transaction_detail_item[8]
                                if "vena" in purchased_by.lower():
                                    purchased_by = "Vena"
                                elif purchased_by.lower() == category_str.lower():
                                    purchased_by = "Me"
                                elif "dawn" in purchased_by.lower():
                                    purchased_by = "Dawn"
                                else:
                                    raise Exception(
                                        f"Unable to determine purchase target for item [{item_name}] in transaction "
                                        f"[{matching_uncategorized_bank_csv_transaction}]"
                                    )
                                category = TransactionCategory.objects.all().get(category=category_str) \
                                    if purchased_by == "Me" else None
                                purchase_target = "Me" if purchased_by != "Dawn" else purchased_by
                                Item(
                                    name=item_name,
                                    price=price.replace("$", ""),
                                    purchased_by=purchased_by,
                                    purchase_target=purchase_target,
                                    category=category,
                                    transaction=matching_uncategorized_bank_csv_transaction,
                                    note=note
                                ).save()
                                item_saved = True
                                last_item += 1
                            if not item_saved:
                                raise Exception(
                                    f"Unable to properly save item [{item_name}] in transaction "
                                    f"[{matching_uncategorized_bank_csv_transaction}]"
                                )
                        # elif "Thermostat for Michael".lower() == category.lower():
                        #     matching_uncategorized_bank_csv_transaction.purchased_by = "Michael"
                        #     categories = TransactionCategory.objects.all().filter(category="Not My Expense")
                        #     matching_uncategorized_bank_csv_transaction.category = categories[0]
                        #     matching_uncategorized_bank_csv_transaction.note = note
                        #     matching_uncategorized_bank_csv_transaction.save()
                        elif "Refund".lower() in category_str.lower():
                            print("Refund")
                            print(legacy_transaction_detail)
                            original_transaction = \
                                BankCSVTransaction.objects.filter(name=name, price=price - (2 * price))[0]
                            ReceiptRefund(
                                original_transaction_in_refund=original_transaction,
                                refund_transaction_in_refund=matching_uncategorized_bank_csv_transaction
                            ).save()
                            matching_uncategorized_bank_csv_transaction.category = original_transaction.category
                            matching_uncategorized_bank_csv_transaction.save()
                        else:
                            if name.lower() == "PAYMENT - THANK YOU".lower():
                                category_str = "Mastercard Payment"
                                categories = TransactionCategory.objects.all().filter(category=category_str)
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
                            matching_uncategorized_bank_csv_transaction.save()
                            # print(f"saving matching bank transaction {matching_uncategorized_bank_csv_transaction}")
                # print(f"{i}-processed {legacy_transaction_detail}")
                i += 1
        return HttpResponseRedirect("/")


class UploadBankCSVTransaction(View):

    def post(self, request):
        credit_card_csv = request.FILES['transactions']
        fs = FileSystemStorage()
        file_name = fs.save(credit_card_csv.name, credit_card_csv)
        with open(file_name, 'r') as credit_card_transactions:
            csvFile = csv.reader(credit_card_transactions)
            for line in csvFile:
                date = None
                try:
                    date = datetime.datetime.strptime(line[0], "%m/%d/%Y").astimezone(
                        pytz.timezone('America/Vancouver')
                    ) + datetime.timedelta(hours=8)
                except ValueError:
                    pass
                if date is not None:
                    BankCSVTransaction(
                        month=date,
                        date=date,
                        payment_method="Mastercard",
                        method_of_transaction=line[1],
                        name=line[2],
                        memo=line[3],
                        price=line[4]
                    ).save()
        return HttpResponseRedirect("/")
