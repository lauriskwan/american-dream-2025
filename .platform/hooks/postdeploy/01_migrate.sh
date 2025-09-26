#!/bin/bash

# Post-deployment script for Django migrations
# This script runs after the application is deployed to AWS

set -e

echo "Starting post-deployment tasks..."

# Activate virtual environment if it exists
if [ -d "/var/app/venv" ]; then
    source /var/app/venv/*/bin/activate
fi

# Change to application directory
cd /var/app/current

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Collect static files (if not using S3)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (for demo purposes)
echo "Creating demo superuser..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@readytable.com', 'admin123')
    print('Demo superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Load sample data if needed
echo "Loading sample menu data..."
python manage.py shell << EOF
from restaurant.models import MenuItem
if not MenuItem.objects.exists():
    MenuItem.objects.bulk_create([
        MenuItem(name='Grilled Salmon', description='Fresh Atlantic salmon with herbs', price=24.99, estimated_prep_time_minutes=18),
        MenuItem(name='Caesar Salad', description='Crisp romaine with parmesan and croutons', price=12.99, estimated_prep_time_minutes=8),
        MenuItem(name='Beef Burger', description='Angus beef with lettuce, tomato, and fries', price=16.99, estimated_prep_time_minutes=15),
        MenuItem(name='Margherita Pizza', description='Fresh mozzarella, basil, and tomato sauce', price=18.99, estimated_prep_time_minutes=12),
        MenuItem(name='Chicken Pasta', description='Grilled chicken with alfredo sauce', price=19.99, estimated_prep_time_minutes=14),
    ])
    print('Sample menu items created')
else:
    print('Menu items already exist')
EOF

echo "Post-deployment tasks completed successfully!"

# AWS ECS deployment considerations:
# - This script would be adapted for ECS container startup
# - Database migrations should be run as a separate ECS task
# - Static files should be served from S3 in production
# - Environment variables should come from AWS Secrets Manager
# - Logging should go to CloudWatch
