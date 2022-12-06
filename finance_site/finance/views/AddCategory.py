from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import TransactionCategory


class AddCategory(View):
    def get(self, request):
        return render(request, 'create_or_update_category.html')

    def post(self, request):
        transaction_category = TransactionCategory(
            category=request.POST['category'],
            starred="starred" in request.POST,
            order_number=request.POST['order_number']
        )
        transaction_category.save()
        return HttpResponseRedirect(transaction_category.get_update_link)
