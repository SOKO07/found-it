from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Category, Item


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'School Email'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@usls.edu.ph'):
            raise ValidationError("Only emails from @usls.edu.ph are allowed.", code='invalid_domain')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ItemForm(forms.ModelForm):
    category_name = forms.CharField(
        max_length=100,
        required=True,
        label="Category",
        widget=forms.TextInput(attrs={'list': 'category-list', 'placeholder': 'Click to see categories..'})
    )

    class Meta:
        model = Item
        fields = ['name', 'description', 'image', 'found_location', 'found_date', 'status']
        widgets = {
            'found_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ItemForm, self).__init__(*args, **kwargs)
        
        # For non-admin users, limit the status choices.
        if user and not user.is_staff:
            self.fields['status'].choices = [
                ('not_at_repository', 'Not at Repository'),
                ('at_repository', 'At Repository'),
            ]


class ItemFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Item name or location...'})
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-inline'}),
        label='Categories'
    )
    found_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Date Found'
    )
    sort_by = forms.ChoiceField(
        choices=(
            ('-found_date', 'Date Found (Newest First)'),
            ('found_date', 'Date Found (Oldest First)'),
            ('-pub_date', 'Date Published (Newest First)'),
            ('pub_date', 'Date Published (Oldest First)'),
            ('name', 'Name (A-Z)'),
            ('-name', 'Name (Z-A)'),
        ),
        required=False,
        label='Sort by'
    )
    include_retrieved = forms.BooleanField(required=False, label='Show Retrieved Items')
