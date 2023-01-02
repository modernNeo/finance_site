from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.urls import path

from finance.url_paths import update_finalized_transaction, update_finalized_item, update_pending_transaction, \
    update_pending_item, update_transaction_refunding_mapping, update_transaction_reimbursement_mapping, \
    update_transaction_repaid_mapping, update_item_refund_mapping, update_item_reimbursement_mapping, \
    update_item_repaid_mapping, update_e_transfer_internal_transfer_mapping, update_category
from finance.views.AddCategory import AddCategory
from finance.views.ImportFromLegacySystem import ImportFromLegacySystem
from finance.views.ListCategories import ListCategories
from finance.views.ListPendingTransactions import ListPendingTransactions
from finance.views.Mappings import Mappings
from finance.views.NewETransferInternalTransferMapping import NewETransferInternalTransferMapping
from finance.views.NewFinalizedItem import NewFinalizedItem
from finance.views.NewItemRefundMapping import NewItemRefundMapping
from finance.views.NewItemReimbursementMapping import NewItemReimbursementMapping
from finance.views.NewItemRepaidMapping import NewItemRepaidMapping
from finance.views.NewPendingItem import NewPendingItem
from finance.views.NewPendingTransaction import NewPendingTransaction
from finance.views.NewTransactionRefundMapping import NewTransactionRefundMapping
from finance.views.NewTransactionReimbursementMapping import NewTransactionReimbursementMapping
from finance.views.NewTransactionRepaidMapping import NewTransactionRepaidMapping
from finance.views.ShowAllDebitCardTransactions import ShowAllDebitCardTransactions
from finance.views.ShowAllMasterCardTransactions import ShowAllMasterCardTransactions
from finance.views.ShowCategorizedDebitCardTransactions import ShowCategorizedDebitCardTransactions
from finance.views.ShowCategorizedMasterCardTransactions import ShowCategorizedMasterCardTransactions
from finance.views.ShowCategorizedTransactions import ShowCategorizedTransactions
from finance.views.ShowItemsAwaitingRepayment import ShowItemsAwaitingRepayment
from finance.views.ShowMasterCardPaymentBreakdown import ShowMasterCardPaymentBreakdown
from finance.views.ShowUnTransferredLegacyDebitCardTransactions import ShowUnTransferredLegacyDebitCardTransactions
from finance.views.ShowUnTransferredLegacyMasterCardTransactions import \
    ShowUnTransferredLegacyMasterCardTransactions
from finance.views.ShowUncategorizedDebitCardTransactions import ShowUncategorizedDebitCardTransactions
from finance.views.ShowUncategorizedMasterCardTransactions import ShowUncategorizedMasterCardTransactions
from finance.views.UpdateCategory import UpdateCategory
from finance.views.UpdateETransferInternalTransferMapping import UpdateETransferInternalTransferMapping
from finance.views.UpdateFinalizedItem import UpdateFinalizedItem
from finance.views.UpdateItemRefundMapping import UpdateItemRefundMapping
from finance.views.UpdateItemReimbursementMapping import UpdateItemReimbursementMapping
from finance.views.UpdateItemRepaidMapping import UpdateItemRepaidMapping
from finance.views.UpdatePendingItem import UpdatePendingItem
from finance.views.UpdatePendingTransaction import UpdatePendingTransaction
from finance.views.UpdateTransaction import UpdateTransaction
from finance.views.UpdateTransactionRefundMapping import UpdateTransactionRefundMapping
from finance.views.UpdateTransactionReimbursementMapping import UpdateTransactionReimbursementMapping
from finance.views.UpdateTransactionRepaidMapping import UpdateTransactionRepaidMapping
from finance.views.UploadDebitCardTransaction import UploadDebitCardTransaction
from finance.views.UploadMasterCardTransaction import UploadMasterCardTransaction

urlpatterns = [
                  path('', login_required(ShowCategorizedTransactions.as_view()), name="index"),
                  path('master_card_payment_breakdown', login_required(ShowMasterCardPaymentBreakdown.as_view()),
                       name="payment_breakdown"),
                  path(f'{update_finalized_transaction}<int:transaction_id>', login_required(UpdateTransaction.as_view()),
                       name="update_finalized_transaction"),
                  path("item/finalized/new", login_required(NewFinalizedItem.as_view()), name="new_finalized_item"),
                  path(f'{update_finalized_item}<int:item_id>', login_required(UpdateFinalizedItem.as_view()), name="update_finalized_item"),
                  path('transaction/pending/new', login_required(NewPendingTransaction.as_view()), name="new_pending_transaction"),
                  path('item/pending/new', login_required(NewPendingItem.as_view()), name="new_pending_item"),
                  path('pending_transactions', login_required(ListPendingTransactions.as_view()), name="list_pending_transactions"),
                  path(f'{update_pending_transaction}<int:pending_transaction_id>', login_required(UpdatePendingTransaction.as_view()),
                       name="update_pending_transaction"),
                  path(f'{update_pending_item}<int:pending_item_id>', login_required(UpdatePendingItem.as_view()),
                       name="update_pending_item"),
                  path('category/add', login_required(AddCategory.as_view()), name="add_category"),
                  path(f"{update_category}<int:category_id>", login_required(UpdateCategory.as_view()), name="update_category"),
                  path("categories", login_required(ListCategories.as_view()), name="list_categories"),
                  path('mappings', login_required(Mappings.as_view()), name="mappings"),
                  path(
                      'mapping/refund/transaction/new',
                      login_required(NewTransactionRefundMapping.as_view()),
                      name="new_transaction_refund_mapping"
                  ),
                  path(
                      'mapping/reimbursement/transaction/new',
                      login_required(NewTransactionReimbursementMapping.as_view()),
                      name="new_transaction_reimbursement_mapping"
                  ),
                  path(
                      'mapping/repaid/transaction/new',
                      login_required(NewTransactionRepaidMapping.as_view()),
                      name="new_transaction_repaid_mapping"),
                  #

                  path('mapping/refund/item/new', login_required(NewItemRefundMapping.as_view()), name="new_item_refund_mapping"),
                  path(
                      'mapping/reimbursement/item/new',
                      login_required(NewItemReimbursementMapping.as_view()),
                      name="new_item_reimbursement_mapping"
                  ),
                  path('mapping/repaid/item/new', login_required(NewItemRepaidMapping.as_view()), name="new_item_refund_mapping"),
                  path(
                      'mapping/e_transfer_internal_transfer_mapping/new',
                      login_required(NewETransferInternalTransferMapping.as_view()),
                      name="new_e_transfer_internal_transfer_mapping"
                  ),
                  path(
                      f'{update_transaction_refunding_mapping}<int:mapping_id>',
                      login_required(UpdateTransactionRefundMapping.as_view()),
                      name="update_transaction_refund_mapping"
                  ),
                  path(
                      f'{update_transaction_reimbursement_mapping}<int:mapping_id>',
                      login_required(UpdateTransactionReimbursementMapping.as_view()),
                      name="update_transaction_reimbursement_mapping"
                  ),
                  path(
                      f'{update_transaction_repaid_mapping}<int:mapping_id>',
                      login_required(UpdateTransactionRepaidMapping.as_view()),
                      name="update_transaction_repaid_mapping"
                  ),
                  #
                  path(
                      f'{update_item_refund_mapping}<int:mapping_id>',
                      login_required(UpdateItemRefundMapping.as_view()),
                      name="update_item_refund_mapping"
                  ),
                  path(
                      f'{update_item_reimbursement_mapping}<int:mapping_id>',
                      login_required(UpdateItemReimbursementMapping.as_view()),
                      name="update_item_reimbursement_mapping"
                  ),
                  path(
                      f'{update_item_repaid_mapping}<int:mapping_id>',
                      login_required(UpdateItemRepaidMapping.as_view()),
                      name="update_item_repaid_mapping"
                  ),
                  #
                  path(
                      f'{update_e_transfer_internal_transfer_mapping}<int:mapping_id>',
                      login_required(UpdateETransferInternalTransferMapping.as_view()),
                      name="update_e_transfer_internal_transfer_mapping"
                  ),
                  path('awaiting_payment', login_required(ShowItemsAwaitingRepayment.as_view()), name='items_awaiting_repayment'),
                  path('legacy_import', login_required(ImportFromLegacySystem.as_view()), name="import_legacy"),
                  path('master_card/all', login_required(ShowAllMasterCardTransactions.as_view()), name="all_master_card"),
                  path('debit_card/all', login_required(ShowAllDebitCardTransactions.as_view()), name="all_debit_card"),
                  path('master_card/categorized', login_required(ShowCategorizedMasterCardTransactions.as_view()),
                       name="categorized_master_card"),
                  path('debit_card/categorized', login_required(ShowCategorizedDebitCardTransactions.as_view()),
                       name="categorized_debit_card"),
                  path(
                      'master_card/uncategorized',
                      login_required(ShowUncategorizedMasterCardTransactions.as_view()),
                      name="uncategorized_mastercard"
                  ),
                  path(
                      'debit_card/uncategorized',
                      login_required(ShowUncategorizedDebitCardTransactions.as_view()),
                      name="uncategorized_debitcard"
                  ),
                  path(
                      'un_transferred_legacy/master_card',
                      login_required(ShowUnTransferredLegacyMasterCardTransactions.as_view()),
                      name="un_transferred_legacy_mastercard"
                  ),
                  path(
                      'un_transferred_legacy/debit_card',
                      login_required(ShowUnTransferredLegacyDebitCardTransactions.as_view()),
                      name="un_transferred_legacy_debitcard"
                  ),
                  # path('transaction/add', add_transaction_view, name="add_transaction"),
                  path('csv/upload/master_card', login_required(UploadMasterCardTransaction.as_view()), name="upload_master_card_csv"),
                  path('csv/upload/debit_card', login_required(UploadDebitCardTransaction.as_view()), name="upload_debit_card_csv")
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
