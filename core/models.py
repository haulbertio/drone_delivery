# In core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('pilot', 'Pilot'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)  # Ensure email is unique
    vessel_callsign = models.CharField(max_length=20, blank=True, null=True)  # Optional for pilots

    # Add custom related_name attributes to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Avoids clash with auth.User.groups
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Avoids clash with auth.User.user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    order_status = models.CharField(max_length=50, default='Pending', choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class DroneMission(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pilot = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'pilot'})
    mission_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
