from .models import CATEGORY
from django import forms

def searchCategories(request):
    return {
        'categories': CATEGORY
    }