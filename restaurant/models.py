from django.db import models
from django.contrib.auth.models import User  # For future Cognito integration
from django.utils import timezone
import random
import string

class RestaurantProfile(models.Model):
    # For a multi-restaurant future, link this with a ForeignKey
    # restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Our Restaurant")
    total_tables = models.PositiveIntegerField(default=20)
    # This would be updated by staff or an automated system in a real app
    currently_occupied_tables = models.PositiveIntegerField(default=15)
    # Average time a party stays at a table, in minutes
    avg_dine_in_duration_minutes = models.PositiveIntegerField(default=45)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # Restaurant's initial guess for prep time
    estimated_prep_time_minutes = models.IntegerField(default=15)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('IN_QUEUE', 'In Queue'),
        ('AWAITING_ARRIVAL', 'Awaiting Arrival'),
        ('RECEIVED', 'Order Received'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Seating'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    # Link to a user profile for the future
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    order_code = models.CharField(max_length=4, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_QUEUE')
    created_at = models.DateTimeField(auto_now_add=True)

    # New queue-based fields
    queue_position = models.PositiveIntegerField(null=True, blank=True)
    # This time is calculated and SET BY THE SYSTEM when the user is notified
    target_arrival_time = models.DateTimeField(null=True, blank=True)

    # Fields for Data Analysis (can be null for now)
    seated_at_time = models.DateTimeField(null=True, blank=True)
    completed_at_time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.generate_order_code()
        if not self.queue_position and self.status == 'IN_QUEUE':
            self.queue_position = self.get_next_queue_position()
        super().save(*args, **kwargs)

    def generate_order_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if not Order.objects.filter(order_code=code).exists():
                return code

    def get_next_queue_position(self):
        last_in_queue = Order.objects.filter(status='IN_QUEUE').order_by('-queue_position').first()
        return (last_in_queue.queue_position + 1) if last_in_queue else 1

    def __str__(self):
        return f"{self.customer_name} - {self.order_code}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"
