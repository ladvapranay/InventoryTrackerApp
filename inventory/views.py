from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .models import InventoryItem, InventoryRequest
from .forms import RequestForm, AdminRequestForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, " ".join(e.messages))
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()
        messages.success(request, "Account created successfully!")
        login(request, user)
        return redirect('dashboard')

    return render(request, 'registration/register.html')

@login_required
def dashboard(request):
    if request.user.is_staff:
        requests = InventoryRequest.objects.all()
        is_admin = True
    else:
        requests = InventoryRequest.objects.filter(requested_by=request.user)
        is_admin = False

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        requests = requests.filter(
            Q(item__name__icontains=search_query) |
            Q(reason__icontains=search_query) |
            Q(priority__icontains=search_query) |
            Q(requested_by__username__icontains=search_query)
        )

    if status_filter:
        requests = requests.filter(status=status_filter)

    requests = requests.order_by('-created_at')

    current_requests_count = requests.exclude(status__in=['Approved', 'Rejected']).count()
    total_requests = requests.count()
    new_count = requests.filter(status='New').count()
    in_progress_count = requests.filter(status='In Progress').count()
    approved_count = requests.filter(status='Approved').count()
    rejected_count = requests.filter(status='Rejected').count()

    paginator = Paginator(requests, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    available_inventories = InventoryItem.objects.all()[:3]

    context = {
        'requests': page_obj,
        'page_obj': page_obj,
        'current_requests_count': current_requests_count,
        'available_inventories': available_inventories,
        'is_admin': is_admin,
        'user_name': request.user.username,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': InventoryRequest.STATUS_CHOICES,
        'total_requests': total_requests,
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }

    return render(request, 'dashboard.html', context)


@login_required
def delete_request(request, request_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to delete this request.")

    inventory_request = get_object_or_404(InventoryRequest, id=request_id)

    if request.method == 'POST':
        inventory_request.delete()
        messages.success(request, f"Request {request_id} has been deleted successfully.")
        return redirect('dashboard')

    return render(request, 'delete_request.html', {'request_id': request_id})


@login_required
def edit_request(request, request_id):
    inventory_request = get_object_or_404(InventoryRequest, id=request_id)

    if inventory_request.requested_by != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to edit this request.")

    if request.method == 'POST':
        form = AdminRequestForm(request.POST, instance=inventory_request) if request.user.is_staff else RequestForm(request.POST, instance=inventory_request)

        if form.is_valid():
            form.save()
            messages.success(request, f"Request {inventory_request.id} updated successfully.")
            return redirect('dashboard')

        messages.error(request, "Failed to update the request. Please correct the errors.")
    else:
        form = AdminRequestForm(instance=inventory_request) if request.user.is_staff else RequestForm(instance=inventory_request)

    return render(request, 'edit_request.html', {
        'form': form,
        'inventory_request': inventory_request,
    })

@login_required
def create_request(request):
    item_id = request.GET.get('item_id')
    prefilled_item = None

    if item_id:
        try:
            prefilled_item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            return HttpResponseBadRequest("Invalid item selected.")

    if request.method == 'POST':
        post_data = request.POST.copy()
        submitted_item_name = post_data.get('item')
        try:
            matching_item = InventoryItem.objects.get(name__iexact=submitted_item_name)
            post_data['item'] = matching_item.id
        except InventoryItem.DoesNotExist:
            form = RequestForm(request.POST)
            form.add_error('item', "The selected item does not exist. Please pick a valid option.")

            messages.error(request, "The selected item does not exist. Please pick a valid option.")

            return render(request, 'create_request.html', {
                'form': form,
                'inventory_items': InventoryItem.objects.all(),
                'selected_item': submitted_item_name
            })

        form = RequestForm(post_data)

        if form.is_valid():
            inventory_request = form.save(commit=False)
            inventory_request.requested_by = request.user
            inventory_request.status = 'New'
            inventory_request.save()

            messages.success(request, "Request created successfully.")
            return redirect('dashboard')

        messages.error(request, "Please correct the errors below.")

        return render(request, 'create_request.html', {
            'form': form,
            'inventory_items': InventoryItem.objects.all(),
            'selected_item': submitted_item_name
        })

    form = RequestForm(initial={'item': prefilled_item})

    return render(request, 'create_request.html', {
        'form': form,
        'inventory_items': InventoryItem.objects.all(),
        'selected_item': prefilled_item.name if prefilled_item else ''
    })


@login_required
def available_inventory(request):
    items = InventoryItem.objects.filter(quantity__gt=0)
    return render(request, 'available_inventory.html', {'items': items})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return render(request, 'registration/logout.html', {'logged_out': True})
    return render(request, 'registration/logout.html', {'logged_out': False})
