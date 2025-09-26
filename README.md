# ReadyTable - Intelligent Virtual Queue System

ReadyTable is a web application that eliminates restaurant wait times through an intelligent virtual queue system. Diners join a queue remotely, place their order, and receive notifications when it's time to arrive - ensuring their table is ready and their food is prepared and ready to be served the moment they sit down.

## 🏗️ Architecture Overview

**Phase 1: Local PoC** - A fully functional queue-based system that runs locally
**Phase 2: AWS Deployment** - Scalable cloud deployment on AWS

### Technology Stack

- **Backend**: Django 4.2.7 with ORM, templates, and admin panel
- **Database**: SQLite (local) / PostgreSQL (AWS RDS)
- **Frontend**: Django Templates with Tailwind CSS
- **Containerization**: Docker and Docker Compose
- **Cloud**: AWS ECS, RDS, S3, Cognito, Amazon Q

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional)
- PostgreSQL (for production-like testing)

### Option 1: Local Python Setup

1. **Clone and setup virtual environment**:
   ```bash
   cd /path/to/American_Dream
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations and setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: create your own admin user
   ```

4. **Start development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the application**:
   - Customer interface: http://localhost:8000/
   - Restaurant login: http://localhost:8000/restaurant/login/
   - Admin panel: http://localhost:8000/admin/

### Option 2: Docker Setup (Recommended)

1. **Start with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - Customer interface: http://localhost:8000/
   - Restaurant login: http://localhost:8000/restaurant/login/
   - Admin panel: http://localhost:8000/admin/

### Demo Credentials

- **Restaurant Staff Login**: `admin` / `admin123`
- **Admin Panel**: `admin` / `admin123`

## 📱 Features

### Customer Experience
- **Live Wait Times**: See current estimated wait before ordering
- **Virtual Queue**: Join queue remotely without physical waiting
- **Order Placement**: Select items while joining the queue
- **Queue Position**: Real-time position tracking with unique order codes
- **Smart Notifications**: System tells you when to head to restaurant
- **Instant Service**: Food is prepared and ready to be served immediately upon seating
- **Order Status**: Track progress from queue to completion

### Restaurant Queue Management
- **Live Queue Dashboard**: View all customers in queue by arrival order
- **Wait Time Display**: Real-time calculation based on capacity and queue
- **Notify System**: One-click to notify next customer to approach
- **Food Preparation Timing**: Coordinate kitchen prep with customer arrival notifications
- **Multi-Status Tracking**: Queue → Awaiting Arrival → Received → Preparing → Ready → Completed
- **Capacity Management**: Configure tables and average dining duration

### AI Co-pilot (Simulated)
- **Queue Analytics**: Insights on wait times and queue efficiency
- **Demand Forecasting**: Predict busy periods and staffing needs
- **Revenue Analytics**: Track sales trends and optimization opportunities

## 🗄️ Database Models

### RestaurantProfile
- `name`: Restaurant name
- `total_tables`: Maximum seating capacity
- `currently_occupied_tables`: Real-time occupied count
- `avg_dine_in_duration_minutes`: Average time customers spend dining

### Order (Refactored for Queue System)
- `customer_name`: Customer identifier
- `order_code`: Unique 4-character code
- `queue_position`: Position in virtual queue (auto-assigned)
- `target_arrival_time`: System-calculated arrival time (set when notified)
- `status`: IN_QUEUE → AWAITING_ARRIVAL → RECEIVED → PREPARING → READY → COMPLETED
- `seated_at_time`: Timestamp when marked READY
- `completed_at_time`: Timestamp when marked COMPLETED

### MenuItem
- `name`: Dish name
- `description`: Detailed description
- `price`: Decimal price
- `estimated_prep_time_minutes`: Kitchen preparation time estimate

### OrderItem
- Links orders to menu items with quantities

## 🔧 Queue System Logic

### Wait Time Calculation
```python
parties_in_queue = Order.objects.filter(status='IN_QUEUE').count()
tables_to_free_up = parties_in_queue + currently_occupied_tables - total_tables
wait_time_minutes = (tables_to_free_up / total_tables) * avg_dine_in_duration_minutes
```

### Customer Flow
1. **View Wait Time**: Customer sees live estimated wait on menu page
2. **Join Queue**: Place order and automatically join virtual queue
3. **Queue Position**: Receive position number and order code
4. **Wait Remotely**: Track status via order code
5. **Notification**: Restaurant notifies when table is ready
6. **Arrival**: Customer arrives just as table and food are prepared

### Restaurant Flow
1. **Queue Management**: View all customers in queue order
2. **Capacity Monitoring**: Track occupied tables and wait times
3. **Notify Next**: Click to notify first customer in queue
4. **Status Updates**: Track customer from notification to completion

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Local Development
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# AWS Production (configure when deploying)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
AWS_STORAGE_BUCKET_NAME=your-s3-bucket
COGNITO_USER_POOL_ID=your-user-pool-id
AWS_Q_API_ENDPOINT=your-q-api-endpoint
```

## ☁️ AWS Deployment Guide

### Prerequisites

- AWS CLI configured
- Docker installed
- ECR repository created
- RDS PostgreSQL instance
- S3 bucket for static files
- Cognito User Pool (optional)

### Step 1: Build and Push Docker Image

```bash
# Build the image
docker build -t readytable .

# Tag for ECR
docker tag readytable:latest YOUR_ECR_URI:latest

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker push YOUR_ECR_URI:latest
```

### Step 2: Configure Environment Variables

Set these in your ECS Task Definition or AWS Systems Manager Parameter Store:

```bash
# Database (from RDS)
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/readytable
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_NAME=readytable
DB_USER=readytable_user
DB_PASSWORD=your-secure-password

# AWS Services
AWS_STORAGE_BUCKET_NAME=your-readytable-bucket
AWS_S3_REGION_NAME=us-east-1
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_APP_CLIENT_ID=your-app-client-id

# Security
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-alb-dns-name
```

### Step 3: ECS Task Definition

Create an ECS task definition with:

- **Image**: Your ECR repository URI
- **CPU/Memory**: 512 CPU units, 1024 MB memory (adjust as needed)
- **Port Mappings**: Container port 8000
- **Environment Variables**: From Step 2
- **Execution Role**: With ECR and CloudWatch permissions
- **Task Role**: With S3, RDS, and Cognito permissions

### Step 4: ECS Service Configuration

- **Cluster**: Create or use existing ECS cluster
- **Service Type**: Fargate
- **Desired Count**: 2+ for high availability
- **Load Balancer**: Application Load Balancer
- **Target Group**: HTTP port 8000
- **Health Check**: `/admin/` endpoint

### Step 5: Database Migration

Run migrations as a one-time ECS task:

```bash
aws ecs run-task \
  --cluster your-cluster \
  --task-definition readytable-migrate \
  --overrides '{
    "containerOverrides": [{
      "name": "readytable",
      "command": ["python", "manage.py", "migrate"]
    }]
  }'
```

### Step 6: Static Files (S3)

Configure Django settings for S3:

```python
# Uncomment in settings.py for production
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

## 🤖 AI Integration (Future)

The AI Co-pilot currently shows simulated responses. For production deployment with Amazon Q:

### Amazon Q Integration Points

1. **API Configuration**:
   ```python
   import boto3
   
   q_client = boto3.client('q-developer', region_name='us-east-1')
   
   def get_ai_insights(query, restaurant_data):
       response = q_client.generate_insights(
           query=query,
           context={
               'restaurant_data': restaurant_data,
               'queue_analytics': get_queue_metrics(),
               'wait_time_trends': get_wait_time_analytics()
           }
       )
       return response['insights']
   ```

2. **Data Context**: The system will provide Amazon Q with:
   - Real-time queue data
   - Wait time patterns
   - Customer arrival analytics
   - Table turnover rates
   - Revenue per queue position

3. **Insight Categories**:
   - Queue optimization strategies
   - Wait time predictions
   - Capacity planning recommendations
   - Customer satisfaction metrics
   - Revenue impact analysis

## 🔐 Security Considerations

### Local Development
- Uses Django's built-in authentication
- SQLite database (not for production)
- Debug mode enabled

### Production (AWS)
- **Authentication**: Amazon Cognito integration planned
- **Database**: RDS with encryption at rest
- **Secrets**: AWS Secrets Manager for credentials
- **Network**: VPC with private subnets for database
- **SSL/TLS**: ALB with SSL termination
- **Static Files**: S3 with CloudFront CDN

## 📊 Monitoring and Logging

### Local Development
- Django debug toolbar
- Console logging
- SQLite database browser

### AWS Production
- **Application Logs**: CloudWatch Logs
- **Metrics**: CloudWatch metrics for ECS, RDS, ALB
- **Queue Metrics**: Custom metrics for wait times and queue length
- **Alerts**: CloudWatch alarms for queue overflow and performance
- **Tracing**: AWS X-Ray for request tracing
- **Health Checks**: ALB health checks and ECS health monitoring

## 🧪 Testing

Run tests locally:

```bash
python manage.py test
```

### Queue System Testing Scenarios
- Multiple customers joining queue simultaneously
- Restaurant notification workflow
- Wait time calculation accuracy
- Queue position updates
- Status transition validation

## 📈 Scaling Considerations

### Horizontal Scaling
- **ECS Service**: Auto Scaling based on queue length and CPU/memory
- **Database**: RDS read replicas for queue analytics
- **CDN**: CloudFront for static asset delivery
- **Caching**: ElastiCache for queue state and wait time calculations

### Performance Optimization
- Database indexing on queue_position and status fields
- Real-time queue updates via WebSockets (future enhancement)
- Async notifications for customer alerts
- Queue analytics pre-computation

---

**ReadyTable** - Eliminating restaurant wait times through intelligent virtual queue management and AI-powered operational insights.
