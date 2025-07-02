from urllib.request import Request

from django.contrib import messages

from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .models import InventoryItem, InventoryRequest
from .forms import RequestForm, AdminRequestForm

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Create user and log them in
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully!")
        login(request, user)
        return redirect('dashboard')

    return render(request, 'registration/register.html')

@login_required
def dashboard(request):
    if request.user.is_staff:
        requests = InventoryRequest.objects.all()
        current_requests_count = InventoryRequest.objects.exclude(status__in=['Approved', 'Rejected']).count()
        is_admin = True
    else:
        requests = InventoryRequest.objects.filter(requested_by=request.user)
        current_requests_count = InventoryRequest.objects.filter(
            requested_by=request.user
        ).exclude(status__in=['Approved', 'Rejected']).count()
        is_admin = False

    # Get available inventories
    available_inventories = InventoryItem.objects.all()[:3]

    # Pass all the required context variables
    context = {
        'requests': requests,
        'current_requests_count': current_requests_count,  # Add this
        'available_inventories': available_inventories,  # Add this
        'is_admin': is_admin,  # Already present
        'user_name': request.user.username if request.user.is_authenticated else "Guest"
    }

    return render(request, 'dashboard.html', context)


@login_required
def delete_request(request, request_id):
    if request.user.is_staff:  # Check if the user is an admin
        try:
            inventory_request = InventoryRequest.objects.get(id=request_id)
        except InventoryRequest.DoesNotExist:
            # Notify the admin if the request doesn't exist
            messages.error(request, f"Request with ID {request_id} does not exist.")
            return redirect('dashboard')
        if request.method == 'POST':  # Handle deletion with confirmation
            inventory_request.delete()
            messages.success(request, f"Request {request_id} has been deleted successfully.")
            return redirect('dashboard')
        return render(request, 'delete_request.html', {'request_id': request_id})
    return HttpResponseBadRequest("You are not authorized to delete this request.")


# Edit Request View
@login_required
def edit_request(request, request_id):
    if request.user.is_staff:  # Allow only admins to edit status
        inventory_request = get_object_or_404(InventoryRequest, id=request_id)
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if new_status and new_status in ['New', 'In Progress', 'Approved', 'Rejected']:
                inventory_request.status = new_status
                inventory_request.save()
                messages.success(request, f"Request {request_id} updated to {new_status}.")
                return redirect('dashboard')
            messages.error(request, "Invalid or missing status!")
        return render(request, 'edit_request.html', {'inventory_request': inventory_request})
    return HttpResponseBadRequest("You are not authorized to edit this request.")

from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest


@login_required
def create_request(request):
    """
    Allow users to create new inventory requests with a free text field or dropdown for items.
    """

    # Pre-fill data in case `item_id` is passed in the URL
    item_id = request.GET.get('item_id')  # Retrieves `item_id` from query parameters
    prefilled_item = None
    if item_id:
        try:
            prefilled_item = InventoryItem.objects.get(id=item_id)
        except InventoryItem.DoesNotExist:
            return HttpResponseBadRequest("Invalid item selected.")

    # Handle form submission
    if request.method == 'POST':
        post_data = request.POST.copy()  # Copy POST data to modify it

        # Retrieve the submitted item name
        submitted_item_name = post_data.get('item')  # Submitted item as plain text
        try:
            # Resolve the item name to an `InventoryItem` instance (case-insensitive)
            matching_item = InventoryItem.objects.get(name__iexact=submitted_item_name)
            post_data['item'] = matching_item.id  # Replace the `item` field with its ID
        except InventoryItem.DoesNotExist:
            # Handle invalid or non-existent item names
            form = RequestForm(request.POST)  # Pass the original POST data with the invalid name
            form.add_error('item', "The selected item does not exist. Please pick a valid option.")
            return render(request, 'create_request.html', {
                'form': form,
                'inventory_items': InventoryItem.objects.all()
            })

        # Now validate the form with the updated POST data
        form = RequestForm(post_data)
        if form.is_valid():
            inventory_request = form.save(commit=False)  # Create the object without saving yet
            inventory_request.requested_by = request.user  # Link the request to the logged-in user
            inventory_request.status = 'New'  # Set the status for new requests
            inventory_request.save()  # Save the new request in the database

            return redirect('dashboard')  # Redirect to the dashboard after successful creation
        else:
            print("Form errors:", form.errors)  # For debugging purposes


    # For GET requests or when the form is invalid
    form = RequestForm(initial={'item': prefilled_item})
    return render(request, 'create_request.html', {
        'form': form,
        'inventory_items': InventoryItem.objects.all()  # Provide items for dropdown suggestions
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
