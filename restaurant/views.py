from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import MenuItem, Order, OrderItem, RestaurantProfile
import json
from datetime import datetime, timedelta

def calculate_estimated_wait_time():
    """Calculate estimated wait time based on queue and restaurant capacity"""
    try:
        restaurant = RestaurantProfile.objects.first()
        if not restaurant:
            return "15-25 minutes"  # Default fallback
        
        parties_in_queue = Order.objects.filter(status='IN_QUEUE').count()
        tables_to_free_up = parties_in_queue + restaurant.currently_occupied_tables - restaurant.total_tables
        
        if tables_to_free_up <= 0:
            return "5-10 minutes"
        
        wait_time_minutes = (tables_to_free_up / restaurant.total_tables) * restaurant.avg_dine_in_duration_minutes
        
        # Format as range
        min_wait = max(5, int(wait_time_minutes * 0.8))
        max_wait = int(wait_time_minutes * 1.2)
        
        return f"{min_wait}-{max_wait} minutes"
    except:
        return "15-25 minutes"

# Customer Views
def menu_view(request):
    """Display menu items and current wait time for customers"""
    menu_items = MenuItem.objects.all()
    estimated_wait = calculate_estimated_wait_time()
    return render(request, 'restaurant/menu.html', {
        'menu_items': menu_items,
        'estimated_wait': estimated_wait
    })

def order_create(request):
    """Handle order creation with queue-based logic"""
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        
        # Create order with IN_QUEUE status
        order = Order.objects.create(
            customer_name=customer_name,
            status='IN_QUEUE'
        )
        
        # Add order items
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                menu_item_id = key.split('_')[1]
                quantity = int(value)
                if quantity > 0:
                    menu_item = MenuItem.objects.get(id=menu_item_id)
                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=quantity
                    )
        
        return render(request, 'restaurant/order_confirmation.html', {
            'order': order,
            'estimated_wait': calculate_estimated_wait_time()
        })
    
    return redirect('menu')

def order_status(request, order_code):
    """Display order status for customers"""
    order = get_object_or_404(Order, order_code=order_code)
    return render(request, 'restaurant/order_status.html', {'order': order})

# Restaurant Views
def restaurant_login(request):
    """Restaurant staff login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('restaurant_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'restaurant/login.html')

@login_required
def restaurant_dashboard(request):
    """Restaurant queue management dashboard"""
    queue_orders = Order.objects.filter(status='IN_QUEUE').order_by('created_at')
    awaiting_orders = Order.objects.filter(status='AWAITING_ARRIVAL').order_by('target_arrival_time')
    active_orders = Order.objects.exclude(status__in=['COMPLETED', 'CANCELLED']).exclude(status='IN_QUEUE')
    
    return render(request, 'restaurant/dashboard.html', {
        'queue_orders': queue_orders,
        'awaiting_orders': awaiting_orders,
        'active_orders': active_orders,
        'estimated_wait': calculate_estimated_wait_time()
    })

@login_required
def notify_diner(request, order_id):
    """Notify diner to approach restaurant"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        # Update order status and set target arrival time
        order.status = 'AWAITING_ARRIVAL'
        order.target_arrival_time = timezone.now() + timedelta(minutes=15)
        order.save()
        
        messages.success(request, f'Diner {order.customer_name} ({order.order_code}) has been notified to approach!')
    
    return redirect('restaurant_dashboard')

@login_required
def update_order_status(request, order_id):
    """Update order status and record timestamps"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        order.status = new_status
        
        # Record timestamps based on status
        if new_status == 'READY':
            order.seated_at_time = timezone.now()
        elif new_status == 'COMPLETED':
            order.completed_at_time = timezone.now()
        
        order.save()
        messages.success(request, f'Order {order.order_code} updated to {new_status}')
    
    return redirect('restaurant_dashboard')

@login_required
def ai_copilot(request):
    """AI Co-pilot simulation for restaurant insights"""
    response_text = ""
    
    if request.method == 'POST':
        query = request.POST.get('query', '').lower()
        
        # Simulated AI responses
        if 'popular' in query and 'dish' in query:
            response_text = """Based on this week's data analysis:

🏆 Most Popular Dishes:
1. Grilled Salmon (32 orders) - 28% of total orders
2. Caesar Salad (24 orders) - 21% of total orders  
3. Beef Burger (19 orders) - 17% of total orders
4. Margherita Pizza (15 orders) - 13% of total orders
5. Chicken Pasta (12 orders) - 11% of total orders

📊 Key Insights:
• Salmon orders increased 15% from last week
• Vegetarian options represent 35% of orders
• Average order value: $28.50
• Peak ordering time: 6:30-7:30 PM"""

        elif 'busy' in query or 'forecast' in query:
            response_text = """Tomorrow's Predicted Busy Periods:

🕐 Peak Hours Forecast:
• 12:00-1:30 PM: HIGH (85% capacity) - Lunch rush
• 6:00-8:30 PM: VERY HIGH (95% capacity) - Dinner peak
• 8:30-9:30 PM: MEDIUM (60% capacity) - Late dinner

⚡ Recommendations:
• Pre-prep 40% more salmon portions
• Schedule extra kitchen staff 5:30-9:00 PM  
• Consider limiting complex dishes during peak hours
• Estimated 120-140 covers tomorrow

📈 Confidence Level: 87% (based on historical patterns + local events)"""

        elif 'revenue' in query or 'sales' in query:
            response_text = """Weekly Revenue Analysis:

💰 This Week's Performance:
• Total Revenue: $8,450 (+12% vs last week)
• Average Order Value: $28.50 (+$2.30)
• Total Orders: 296 (+8% vs last week)
• Peak Day: Saturday ($1,680)

📊 Category Breakdown:
• Mains: $5,070 (60%)
• Appetizers: $1,520 (18%)
• Beverages: $1,180 (14%)
• Desserts: $680 (8%)

🎯 Growth Opportunities:
• Upsell beverages (+15% potential)
• Promote dessert pairings
• Weekend brunch expansion"""

        else:
            response_text = """I can help you analyze your restaurant data! Try asking:

• "What were my most popular dishes this week?"
• "Forecast my busiest time tomorrow"  
• "Show me revenue trends"
• "Analyze customer wait times"
• "Recommend menu optimizations"

💡 Tip: I analyze real-time data including order patterns, prep times, customer feedback, and seasonal trends to provide actionable insights."""

    return render(request, 'restaurant/ai_copilot.html', {'response': response_text})

# Placeholder for future Amazon Q integration
def get_ai_insights(query):
    """
    Placeholder function for Amazon Q API integration
    
    Future implementation will:
    1. Send query to Amazon Q Developer Pro API
    2. Include restaurant data context
    3. Return AI-generated insights
    
    Example API call structure:
    
    import boto3
    
    q_client = boto3.client('q-developer', region_name='us-east-1')
    
    response = q_client.generate_insights(
        query=query,
        context={
            'restaurant_data': get_restaurant_analytics(),
            'menu_items': list(MenuItem.objects.values()),
            'recent_orders': list(Order.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values())
        }
    )
    
    return response['insights']
    """
    pass
