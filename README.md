# ReadyTable - Intelligent Dine-in Pre-ordering System

ReadyTable is a web application that allows diners to pre-order meals for a timed, dine-in experience, eliminating wait times. The platform leverages data analytics and generative AI to provide intelligent insights and operational efficiencies for partner restaurants.

## 🏗️ Architecture Overview

**Phase 1: Local PoC** - A fully functional version that runs locally
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
- **Menu Browsing**: View available dishes with descriptions and prices
- **Timed Ordering**: Select arrival time for dine-in experience
- **Order Confirmation**: Receive unique 4-character order code
- **Real-time Status**: Track order preparation status

### Restaurant Dashboard
- **Order Management**: View orders sorted by arrival time
- **Status Updates**: Update order status with automatic timestamp recording
- **Real-time Dashboard**: Auto-refreshing interface for kitchen staff
- **Quick Stats**: Overview of active orders and system status

### AI Co-pilot (Simulated)
- **Intelligent Insights**: Ask questions about restaurant operations
- **Popular Dishes Analysis**: Get data on best-selling items
- **Demand Forecasting**: Predict busy periods and staffing needs
- **Revenue Analytics**: Track sales trends and optimization opportunities

## 🗄️ Database Models

### MenuItem
- `name`: Dish name
- `description`: Detailed description
- `price`: Decimal price
- `estimated_prep_time_minutes`: Kitchen preparation time estimate

### Order
- `customer_name`: Customer identifier
- `order_code`: Unique 4-character code
- `estimated_arrival_time`: When customer plans to arrive
- `status`: RECEIVED → PREPARING → READY → COMPLETED
- `seated_at_time`: Timestamp when marked READY
- `completed_at_time`: Timestamp when marked COMPLETED

### OrderItem
- Links orders to menu items with quantities

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
               'menu_items': get_menu_analytics(),
               'order_history': get_order_analytics()
           }
       )
       return response['insights']
   ```

2. **Data Context**: The system will provide Amazon Q with:
   - Real-time order data
   - Menu performance metrics
   - Customer timing patterns
   - Revenue analytics
   - Seasonal trends

3. **Insight Categories**:
   - Popular dish analysis
   - Demand forecasting
   - Revenue optimization
   - Operational efficiency
   - Customer behavior patterns

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
- **Alerts**: CloudWatch alarms for errors and performance
- **Tracing**: AWS X-Ray for request tracing
- **Health Checks**: ALB health checks and ECS health monitoring

## 🧪 Testing

Run tests locally:

```bash
python manage.py test
```

For production deployment, consider:
- Unit tests for models and views
- Integration tests for API endpoints
- Load testing for peak capacity planning
- Security testing for authentication flows

## 📈 Scaling Considerations

### Horizontal Scaling
- **ECS Service**: Auto Scaling based on CPU/memory
- **Database**: RDS read replicas for read-heavy workloads
- **CDN**: CloudFront for static asset delivery
- **Caching**: ElastiCache for session and query caching

### Performance Optimization
- Database indexing on frequently queried fields
- Connection pooling for database connections
- Async task processing for heavy operations
- Image optimization for menu photos

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the GitHub Issues page
2. Review the AWS deployment logs in CloudWatch
3. Verify environment variable configuration
4. Test with local Docker setup first

---

**ReadyTable** - Transforming the dining experience through intelligent pre-ordering and AI-powered restaurant insights.
