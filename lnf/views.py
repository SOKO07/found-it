from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Case, When, Value, BooleanField
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView

from .models import Category, Item, PendingCategory
from .forms import ItemForm, SignUpForm, ItemFilterForm, LoginForm # Import LoginForm

def _filter_and_sort_items(request):
    """Helper function to filter and sort items based on form data."""
    item_list = Item.objects.all().select_related('category').prefetch_related('held_by')
    # We pass the data to the form for validation and cleaning
    form = ItemFilterForm(request.GET)

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
            item_list = item_list.filter(category__in=categories)

        if found_date:
            item_list = item_list.filter(found_date=found_date)
        
        sort_order = sort_by if sort_by else '-found_date'

        # Annotate with a boolean indicating if the item is held by the current user
        # This allows sorting held items first without separate queries
        if request.user.is_authenticated:
            item_list = item_list.annotate(
                is_held_by_user=Case(
                    When(held_by=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )


        # Determine the ordering expression for case-insensitive sorting
        if sort_order == 'name':
            order_expression = Lower('name')
        elif sort_order == '-name':
            order_expression = Lower('name').desc()
        else:
            order_expression = sort_order

        # Apply the secondary sort order after prioritizing held items
        if request.user.is_authenticated:
            item_list = item_list.order_by('-is_held_by_user', order_expression)
        else:
            item_list = item_list.order_by(order_expression)
    
    return item_list.distinct(), form

def index(request):
    """Main view to display the filter form and the list of items."""
    item_list, form = _filter_and_sort_items(request)
    view_type = request.GET.get('viewMode', 'list') # Get viewMode from URL param or default
    context = {
        'form': form,
        'item_list': item_list,
        'view_type': view_type,
    }
    return render(request, 'lnf/index.html', context)

def items_api(request):
    """API endpoint to fetch filtered and sorted items as HTML."""
    item_list, _ = _filter_and_sort_items(request)
    view_type = request.GET.get('viewMode', 'list') # Get viewMode from AJAX request
    # We need the request object in the template for user-specific logic (e.g., hold/unhold buttons)
    html = render_to_string('lnf/partials/_item_list.html', {'item_list': item_list, 'view_type': view_type}, request=request)
    return JsonResponse({'html': html})



@login_required
def upload(request):
    # Pass the list of approved categories for the datalist
    category_list = Category.objects.all()
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, user=request.user)
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
            messages.success(request, 'Thank you for your honesty. Please proceed to the Liceo Prefect Office to surrender the item.')
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

class Login(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)  # Expire session on browser close
        return super().form_valid(form)

@login_required
def profile(request):
    uploaded_items = request.user.uploaded_items.all()
    watched_items = request.user.held_items.all()
    context = {
        'uploaded_items': uploaded_items,
        'watched_items': watched_items,
    }
    return render(request, 'lnf/profile.html', context)

from django.views.decorators.csrf import csrf_protect

@csrf_protect
@login_required
def toggle_watch_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.user in item.held_by.all():
        item.held_by.remove(request.user)
        watched = False
    else:
        item.held_by.add(request.user)
        watched = True
    return JsonResponse({'status': 'ok', 'watched': watched})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if request.user == item.uploaded_by and item.status != 'retrieved':
        item.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this item.'})

@login_required
def go_to_my_uploads(request):
    return redirect('lnf:profile')

def about(request):
    return render(request, 'lnf/info/about.html')

def features(request):
    return render(request, 'lnf/info/features.html')

def contact(request):
    return render(request, 'lnf/info/contact.html')

def full_info(request):
    return render(request, 'lnf/info/full_info.html')

