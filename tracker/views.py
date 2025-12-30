from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import json

from .models import User, Transaction

# Create your views here.

def index(request):
        return render(request, "tracker/index.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "tracker/register.html", {
                "message" : "Passwords must match!"
            })
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse(index))
        except IntegrityError:
            return render(request, "tracker/register.html", {
                "message" : "Username already taken!"
            })
        
    else:
        return render(request, "tracker/register.html")
    
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(index))
        else:
            return render(request, "tracker/login.html", {
                "message" : "Invalid username or password"
            })

    else:
        return render(request, "tracker/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse(index))

@login_required
def transaction(request):
    categories = Transaction.CATEGORY_CHOICES

    recent = Transaction.objects.filter(user=request.user).order_by('-date')[:4]

    if request.method == "POST":
        rupee = request.POST.get("rupee")
        paise = request.POST.get("paise")
        transaction = request.POST.get("type")
        category = request.POST.get("choice")
        description = request.POST.get("description")
        date = request.POST.get("date")

        if not rupee or not paise or not transaction or not category or not date:
            return render(request, "tracker/transaction.html", {
                "message" : "Some fields are missing!",
                "categories" : categories,
                "recent" : recent
            })

        try :
            amount = round((float(f"{rupee}.{paise}")),2)
        except ValueError:
            return render(request, "tracker/transaction.html", {
                "message" : "Invaild Amount!",
                "categories" : categories,
                "recent" : recent
            })
        
        Transaction.objects.create(
            user=request.user,
            amount=amount,
            transaction=transaction,
            category=category,
            description=description,
            date=date
        )

        return render(request, "tracker/transaction.html", {
            "categories" : categories,
            "recent" : recent
        })

        

    else:
        return render(request, "tracker/transaction.html", {
            "categories" : categories,
            "recent" : recent
        })
    
@login_required
def profile(request):
    user = request.user
    recent = Transaction.objects.filter(user=request.user).order_by('-date')[:4]

    if request.method == "POST":
        username = request.POST.get("username")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if username != user.username:
            user.username = username

        if firstname != user.first_name:
            user.first_name = firstname

        if lastname != user.last_name:
            user.last_name = lastname

        if password and password != "**********":
            if password == confirm:
                user.set_password(password)
                update_session_auth_hash(request, user)
            else:
                message = "Passwords do not match"
                return render(request, "tracker/profile.html", {
                    "user" : user,
                    "recent" : recent,
                    "message" : message
                })
            
        user.save()
        return redirect('profile')
    
    else:
        return render(request, "tracker/profile.html", {
            "user" : user,
            "recent" : recent
        })
    
@login_required
def dashboard(request):
    user = request.user
    selected_category = request.GET.get("category")
    selected_type = request.GET.get("transaction_type")

    transactions = Transaction.objects.filter(user=user)

    if selected_category:
        transactions = transactions.filter(category=selected_category)
    if selected_type:
        transactions = transactions.filter(transaction=selected_type)

    # show all possible categories (from model choices) so edit forms can show every option
    categories = [choice[0] for choice in Transaction.CATEGORY_CHOICES]

    spending_data = transactions.filter(transaction="DEBITED").values('category').annotate(total=Sum('amount')).order_by('category')
    saving_data = transactions.filter(transaction="CREDITED").values('category').annotate(total=Sum('amount')).order_by('category')

    spending_labels = [item['category'] for item in spending_data]
    spending_values = [float(item['total']) for item in spending_data]

    saving_labels = [item['category'] for item in saving_data]
    saving_values = [float(item['total']) for item in saving_data]

    return render(request, 'tracker/dashboard.html', {
        "recent": transactions.order_by('-date'),
        "categories": categories,
        "selected": selected_category,
        "selected_type": selected_type,
        'spending_labels': json.dumps(spending_labels),
        'spending_values': json.dumps(spending_values),
        'saving_labels': json.dumps(saving_labels),
        'saving_values': json.dumps(saving_values),
    })


@login_required
def edit_transaction(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    txn = get_object_or_404(Transaction, pk=id, user=request.user)

    rupee = request.POST.get("rupee")
    paise = request.POST.get("paise")
    transaction_type = request.POST.get("type")
    category = request.POST.get("category")
    description = request.POST.get("description")
    date = request.POST.get("date")

    if not rupee or not paise or not transaction_type or not category or not date:
        return JsonResponse({"error": "Missing fields"}, status=400)

    try:
        amount = round((float(f"{rupee}.{paise}")), 2)
    except ValueError:
        return JsonResponse({"error": "Invalid amount"}, status=400)

    txn.amount = amount
    txn.transaction = transaction_type
    txn.category = category
    txn.description = description
    txn.date = date
    txn.save()

    return JsonResponse({
        "id": txn.id,
        "day": txn.date.day,
        "month": txn.date.strftime('%b'),
        "year": txn.date.year,
        "amount": float(txn.amount),
        "category": txn.category,
        "description": txn.description,
        "transaction": txn.transaction,
    })


@login_required
def delete_transaction(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    txn = get_object_or_404(Transaction, pk=id, user=request.user)
    txn.delete()
    return JsonResponse({"success": True})

def custom_404(request, exception):
    return render(request, "tracker/404.html", status=404)