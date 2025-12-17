from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Category, Item, PendingCategory
from .forms import ItemForm, SignUpForm, ItemFilterForm

def _filter_and_sort_items(data):
    """Helper function to filter and sort items based on form data."""
    item_list = Item.objects.all()
    # We pass the data to the form for validation and cleaning
    form = ItemFilterForm(data)

    if form.is_valid():
        query = form.cleaned_data.get('q')
        categories = form.cleaned_data.get('categories')
        found_date = form.cleaned_data.get('found_date')
        sort_by = form.cleaned_data.get('sort_by')
        include_retrieved = form.cleaned_data.get('include_retrieved')

        if not include_retrieved:
            item_list = item_list.exclude(status='retrieved')

        if query:
            item_list = item_list.filter(
                Q(name__icontains=query) | 
                Q(found_location__icontains=query) |
                Q(pending_category_name__icontains=query)
            )
        
        if categories:
            # Filter by items whose category is in the selected categories
            item_list = item_list.filter(category__in=categories)

        if found_date:
            item_list = item_list.filter(found_date=found_date)
        
        if sort_by:
            item_list = item_list.order_by(sort_by)
        else:
            # Default sort if none is provided
            item_list = item_list.order_by('-found_date')

    return item_list, form

def index(request):
    """Main view to display the filter form and the list of items."""
    item_list, form = _filter_and_sort_items(request.GET)
    context = {
        'form': form,
        'item_list': item_list,
    }
    return render(request, 'lnf/index.html', context)

def items_api(request):
    """API endpoint to fetch filtered and sorted items as HTML."""
    item_list, _ = _filter_and_sort_items(request.GET)
    # We need the request object in the template for user-specific logic (e.g., hold/unhold buttons)
    html = render_to_string('lnf/partials/_item_list.html', {'item_list': item_list, 'request': request})
    return JsonResponse({'html': html})

def base(request):
    return render(request, 'lnf/base.html')

@login_required
def upload(request):
    # Pass the list of approved categories for the datalist
    category_list = Category.objects.all()
    
    if request.method == 'POST':
        form = ItemForm(request.POST, user=request.user)
        if form.is_valid():
            item = form.save(commit=False)
            item.pub_date = timezone.now()
            item.uploaded_by = request.user

            category_name = form.cleaned_data['category_name'].strip()
            try:
                # Check if an approved category already exists.
                category = Category.objects.get(name__iexact=category_name)
                item.category = category
            except Category.DoesNotExist:
                # If not, find or create a pending category.
                pending_category, _ = PendingCategory.objects.get_or_create(
                    name__iexact=category_name, 
                    defaults={'name': category_name}
                )
                item.pending_category_name = pending_category.name
            
            item.save()
            return redirect('lnf:index')
    else:
        form = ItemForm(user=request.user)

    context = {
        "form": form,
        "category_list": category_list,
    }
    return render(request, 'lnf/upload.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lnf:index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def hold_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item.held_by.add(request.user)
    return redirect('lnf:index')

@login_required
def unhold_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    item.held_by.remove(request.user)
    return redirect('lnf:index')
