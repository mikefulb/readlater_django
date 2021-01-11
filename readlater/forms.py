from django import forms
from crispy_forms.helper import FormHelper

from .models import Article, Category


class ArticleCreateForm(forms.ModelForm):
    """Form for creating a new Article."""

    # optional hidden field holding the next url to visit after form submission
    next = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'priority', 'notes', 'next']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)


class ArticleEditForm(forms.ModelForm):
    """Form for editing an existing Article record."""

    # optional hidden field holding the next url to visit after form submission
    next = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'priority', 'progress', 'notes', 'next']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)

        # order category field options by name
        self.fields['category'].queryset = self.fields['category'].queryset.order_by('name')


class CategoryCreateForm(forms.ModelForm):
    """Form for creating a new Category."""
    class Meta:
        model = Category
        fields = ['name']


class CategoryEditForm(forms.ModelForm):
    """Form for editing an existing Category."""

    class Meta:
        model = Category
        fields = ['name']
