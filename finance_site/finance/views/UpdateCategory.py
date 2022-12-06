from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from finance.models.TransactionModels import TransactionCategory


class UpdateCategory(View):
    def get(self, request, category_id):
        transaction_category = TransactionCategory.objects.get(id=category_id)
        return render(
            request, 'create_or_update_category.html',
            context={"transaction_category": transaction_category}
        )

    def post(self, request, category_id):
        transaction_category = TransactionCategory.objects.get(id=category_id)
        transaction_category.category=request.POST['category']
        transaction_category.starred="starred" in request.POST
        transaction_category.order_number=request.POST['order_number']
        transaction_category.save()
        return HttpResponseRedirect(transaction_category.get_update_link)
