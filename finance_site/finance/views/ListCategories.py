from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import TransactionCategory


class ListCategories(View):
    def get(self, request):
        transactions = list(TransactionCategory.objects.filter(order_number__isnull=False).order_by('order_number'))
        transactions.extend(list(TransactionCategory.objects.filter(order_number__isnull=True)))
        return render(request,
                      'list_of_categories.html',
                      context={
                          "categories": transactions,
                          "current_page" : "categories"
                      }
                      )
