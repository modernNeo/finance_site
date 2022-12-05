from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from finance.url_paths import update_bank_transaction, update_bank_item, update_pending_transaction, \
    update_pending_item, update_transaction_refunding_mapping, update_transaction_reimbursement_mapping, \
    update_transaction_repaid_mapping, update_item_refund_mapping, update_item_reimbursement_mapping, \
    update_item_repaid_mapping, update_e_transfer_internal_transfer_mapping
from finance.views.ImportFromLegacySystem import ImportFromLegacySystem
from finance.views.ListPendingTransactions import ListPendingTransactions
from finance.views.Mappings import Mappings
from finance.views.NewETransferInternalTransferMapping import NewETransferInternalTransferMapping
from finance.views.NewItemRefundMapping import NewItemRefundMapping
from finance.views.NewItemReimbursementMapping import NewItemReimbursementMapping
from finance.views.NewItemRepaidMapping import NewItemRepaidMapping
from finance.views.NewPendingItem import NewPendingItem
from finance.views.NewPendingTransaction import NewPendingTransaction
from finance.views.NewTransactionRefundMapping import NewTransactionRefundMapping
from finance.views.NewTransactionReimbursementMapping import NewTransactionReimbursementMapping
from finance.views.NewTransactionRepaidMapping import NewTransactionRepaidMapping
from finance.views.ShowCategorizedTransactions import ShowCategorizedTransactions
from finance.views.ShowDebitCardTransactions import ShowDebitCardTransactions
from finance.views.ShowItemsAwaitingRepayment import ShowItemsAwaitingRepayment
from finance.views.ShowMasterCardPaymentBreakdown import ShowMasterCardPaymentBreakdown
from finance.views.ShowMasterCardTransactions import ShowMasterCardTransactions
from finance.views.ShowUnTransferredLegacyDebitCardTransactions import ShowUnTransferredLegacyDebitCardTransactions
from finance.views.ShowUnTransferredLegacyMasterCardTransactions import \
    ShowUnTransferredLegacyMasterCardTransactions
from finance.views.ShowUncategorizedDebitCardTransactions import ShowUncategorizedDebitCardTransactions
from finance.views.ShowUncategorizedMasterCardTransactions import ShowUncategorizedMasterCardTransactions
from finance.views.UpdateETransferInternalTransferMapping import UpdateETransferInternalTransferMapping
from finance.views.UpdateItem import UpdateItem
from finance.views.UpdateItemRefundMapping import UpdateItemRefundMapping
from finance.views.UpdateItemReimbursementMapping import UpdateItemReimbursementMapping
from finance.views.UpdateItemRepaidMapping import UpdateItemRepaidMapping
from finance.views.UpdatePendingItem import UpdatePendingItem
from finance.views.UpdatePendingTransaction import UpdatePendingTransaction
from finance.views.UpdateTransaction import UpdateTransaction
from finance.views.UpdateTransactionRefundMapping import UpdateTransactionRefundMapping
from finance.views.UpdateTransactionReimbursementMapping import UpdateTransactionReimbursementMapping
from finance.views.UpdateTransactionRepaidMapping import UpdateTransactionRepaidMapping



urlpatterns = [
    path('', ShowCategorizedTransactions.as_view(), name="index"),
    path('master_card_payment_breakdown', ShowMasterCardPaymentBreakdown.as_view(), name="payment_breakdown"),
    path('master_card', ShowMasterCardTransactions.as_view(), name="categorized_master_card"),
    path('debit_card', ShowDebitCardTransactions.as_view(), name="categorized_debit_card"),

    path(f'{update_bank_transaction}<int:transaction_id>', UpdateTransaction.as_view(), name="update_bank_transaction"),
    path(f'{update_bank_item}<int:item_id>', UpdateItem.as_view(), name="update_item"),

    path('transaction/pending/new', NewPendingTransaction.as_view(), name="new_pending_transaction"),
    path('item/pending/new', NewPendingItem.as_view(), name="new_pending_item"),
    path('pending_transactions', ListPendingTransactions.as_view(), name="list_pending_transactions"),
    path(f'{update_pending_transaction}<int:pending_transaction_id>', UpdatePendingTransaction.as_view(), name="update_pending_transaction"),
    path(f'{update_pending_item}<int:pending_item_id>', UpdatePendingItem.as_view(), name="update_pending_item"),

    path('mappings', Mappings.as_view(), name="mappings"),
    path(
        'mapping/refund/transaction/new',
         NewTransactionRefundMapping.as_view(),
        name="new_transaction_refund_mapping"
    ),
    path(
        'mapping/reimbursement/transaction/new',
        NewTransactionReimbursementMapping.as_view(),
        name="new_transaction_reimbursement_mapping"
    ),
    path(
        'mapping/repaid/transaction/new',
        NewTransactionRepaidMapping.as_view(),
        name="new_transaction_repaid_mapping"),
    #

    path('mapping/refund/item/new', NewItemRefundMapping.as_view(), name="new_item_refund_mapping"),
    path(
        'mapping/reimbursement/item/new',
        NewItemReimbursementMapping.as_view(),
        name="new_item_reimbursement_mapping"
    ),
    path('mapping/repaid/item/new', NewItemRepaidMapping.as_view(), name="new_item_refund_mapping"),
    path(
        'mapping/e_transfer_internal_transfer_mapping/new',
        NewETransferInternalTransferMapping.as_view(),
        name="new_e_transfer_internal_transfer_mapping"
    ),
    path(
        f'{update_transaction_refunding_mapping}<int:mapping_id>',
        UpdateTransactionRefundMapping.as_view(),
        name="update_transaction_refund_mapping"
    ),
    path(
        f'{update_transaction_reimbursement_mapping}<int:mapping_id>',
        UpdateTransactionReimbursementMapping.as_view(),
        name="update_transaction_reimbursement_mapping"
    ),
    path(
        f'{update_transaction_repaid_mapping}<int:mapping_id>',
        UpdateTransactionRepaidMapping.as_view(),
        name="update_transaction_repaid_mapping"
    ),
    #
    path(
        f'{update_item_refund_mapping}<int:mapping_id>',
        UpdateItemRefundMapping.as_view(),
        name="update_item_refund_mapping"
    ),
    path(
        f'{update_item_reimbursement_mapping}<int:mapping_id>',
        UpdateItemReimbursementMapping.as_view(),
        name="update_item_reimbursement_mapping"
    ),
    path(
        f'{update_item_repaid_mapping}<int:mapping_id>',
        UpdateItemRepaidMapping.as_view(),
        name="update_item_repaid_mapping"
    ),
    #
    path(
        f'{update_e_transfer_internal_transfer_mapping}<int:mapping_id>',
        UpdateETransferInternalTransferMapping.as_view(),
        name="update_e_transfer_internal_transfer_mapping"
    ),
    path('awaiting_payment', ShowItemsAwaitingRepayment.as_view(), name='items_awaiting_repayment'),
    path('legacy_import', ImportFromLegacySystem.as_view(), name="import_legacy"),
    path(
        'uncategorized/master_card',
        ShowUncategorizedMasterCardTransactions.as_view(),
        name="uncategorized_transactions_mastercard"
    ),
    path(
        'uncategorized/debit_card',
        ShowUncategorizedDebitCardTransactions.as_view(),
        name="uncategorized_transactions_debitcard"
    ),
    path(
        'un_transferred_legacy/master_card',
        ShowUnTransferredLegacyMasterCardTransactions.as_view(),
        name="un_transferred_legacy_mastercard"
    ),
    path(
        'un_transferred_legacy/debit_card',
        ShowUnTransferredLegacyDebitCardTransactions.as_view(),
        name="un_transferred_legacy_debitcard"
    ),
    # path('transaction/add', add_transaction_view, name="add_transaction"),
    # path('csv/upload/credit_card', UploadBankCSVTransaction.as_view(), name="add_transaction"),
    # path('csv/upload/debit_card', UploadBankCSVTransaction.as_view(), name="add_transaction")
] +  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
