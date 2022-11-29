from django.urls import path

from finance_site.views import add_transaction_view, UploadBankCSVTransaction, \
    LinkUnlinkedLegacyTransactionDetailsCSVTransactions, ShowUncategorizedTransactions, ShowCategorizedTransactions, \
    ImportFromLegacySystem

urlpatterns = [
    path('', ShowCategorizedTransactions.as_view(), name="index"),
    path('legacy_import', ImportFromLegacySystem.as_view(), name="import_legacy"),
    path('uncategorized', ShowUncategorizedTransactions.as_view(), name="uncategorized_transactions"),
    path('unfinalized', LinkUnlinkedLegacyTransactionDetailsCSVTransactions.as_view(), name="index"),
    # path('transaction/add', add_transaction_view, name="add_transaction"),
    path('csv/upload/credit_card', UploadBankCSVTransaction.as_view(), name="add_transaction"),
    # path('csv/upload/transaction_details', UploadLegacyTransactionDetailsCSV.as_view(), name="add_transaction")
]