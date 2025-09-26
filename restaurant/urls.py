from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Customer URLs
    path('', views.menu_view, name='menu'),
    path('order/', views.order_create, name='order_create'),
    path('status/<str:order_code>/', views.order_status, name='order_status'),
    
    # Restaurant URLs
    path('restaurant/login/', views.restaurant_login, name='restaurant_login'),
    path('restaurant/logout/', LogoutView.as_view(next_page='restaurant_login'), name='restaurant_logout'),
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant/order/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('restaurant/order/<int:order_id>/notify/', views.notify_diner, name='notify_diner'),
    path('restaurant/ai-copilot/', views.ai_copilot, name='ai_copilot'),
]
