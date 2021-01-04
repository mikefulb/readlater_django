from django import forms
from crispy_forms.helper import FormHelper

from .models import Article, Category


class ArticleCreateForm(forms.ModelForm):
    """Form for creating a new Article."""

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'priority', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)


class ArticleEditForm(forms.ModelForm):
    """Form for editing an existing Article record."""

    class Meta:
        model = Article
        fields = ['name', 'url', 'category', 'priority', 'progress', 'notes']

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
