from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass

class Transaction(models.Model):
    TRANSACTION_TYPES = [('CREDITED', 'Credited'), ('DEBITED', 'Debited')]

    CATEGORY_CHOICES = [('FOOD', 'Food'), ('RENT', 'Rent'), ('SALARY', 'Salary'), ('TRAVEL', 'Travel'), ('SHOPPING', 'Shopping'), ('ENTERTAINMENT', 'Entertainment'), ('MEDICAL', 'Medical'), ('UTILITIES', 'Utilities'), ('EDUCATION', 'Education'), ('TRANSPORT', 'Transport'), ('GROCERIES', 'Groceries'), ('INVESTMENT', 'Investment'), ('INSURANCE', 'Insurance'), ('GIFT', 'Gifts'), ('FEES', 'Fees'), ('TAX', 'Taxes'), ('SAVINGS', 'Savings'), ('BONUS', 'Bonus'), ('OTHER', 'Other'),]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    transaction = models.CharField(max_length=8, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)



