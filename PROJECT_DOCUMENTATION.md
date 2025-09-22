# MineFlow - Mining Operations Management System

## Project Overview

MineFlow is a comprehensive web-based mining operations management system built with Django REST Framework (backend) and React (frontend). The system manages the complete workflow of mining operations including truck dispatch, order management, customer relations, and real-time tracking.

## Technology Stack

### Backend
- **Django 5.2.6** - Web framework
- **Django REST Framework** - API development
- **MySQL** - Database (Hostinger hosted)
- **JWT Authentication** - Token-based auth
- **CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - Frontend framework
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Recharts** - Data visualization

## Project Structure

```
mineflow/
├── backend/                    # Django backend application
│   ├── __init__.py
│   ├── settings.py            # Django configuration
│   ├── urls.py               # Main URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
│
├── api/                       # Main Django app
│   ├── models.py             # Database models
│   ├── views.py              # API views and ViewSets
│   ├── serializers.py        # Data serialization
│   ├── urls.py               # API URL routing
│   ├── admin.py              # Django admin configuration
│   └── management/
│       └── commands/         # Custom Django commands
│           ├── create_admin.py
│           ├── clear_database.py
│           └── clear_database_sql.py
│
├── frontend/                  # React frontend application
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── AdminDashboard.js    # Admin interface
│   │   │   ├── OperatorDashboard.js # Operator interface
│   │   │   ├── Login.js             # Authentication
│   │   │   ├── Signup.js            # User registration
│   │   │   ├── ProtectedRoute.js    # Route protection
│   │   │   └── ImageUpload.js       # File upload component
│   │   ├── contexts/
│   │   │   └── AuthContext.js       # Authentication context
│   │   ├── services/
│   │   │   └── api.js               # API service layer
│   │   ├── App.js                   # Main App component
│   │   └── index.js                 # Entry point
│   ├── package.json          # Frontend dependencies
│   └── README.md
│
├── media/                     # User uploaded files
├── staticfiles/              # Static files collection
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Database Models

### Core Models

1. **User & UserProfile**
   - Extended Django User model with role-based permissions
   - Roles: `admin`, `operator`

2. **Customer**
   - Customer information management
   - Fields: name, contact, email, timestamps

3. **Truck**
   - Fleet management
   - Fields: number_plate, capacity, driver_name, status
   - Status: `idle`, `in_transit`

4. **Order**
   - Customer orders
   - Fields: customer, material_type, quantity, status
   - Status: `pending`, `in_progress`, `completed`, `cancelled`

5. **Dispatch**
   - Workflow management
   - Fields: truck, order, operator, status, workflow timestamps
   - Status: `assigned`, `in_transit`, `weigh_in`, `unload`, `weigh_out`, `completed`, `cancelled`

6. **Material**
   - Inventory management
   - Fields: name, stock_quantity, unit

7. **DispatchMedia**
   - Image/document attachments
   - Fields: dispatch, media_type, image, description, uploaded_by

8. **ExceptionLog**
   - Issue tracking
   - Fields: dispatch, description, exception_type, resolved status

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile
- `POST /api/auth/refresh/` - Token refresh

### Core Resources
- `GET/POST /api/customers/` - Customer management
- `GET/POST /api/trucks/` - Truck management
- `GET/POST /api/orders/` - Order management
- `GET/POST /api/dispatches/` - Dispatch management
- `GET/POST /api/materials/` - Material management
- `GET/POST /api/exceptions/` - Exception management

### Specialized Endpoints
- `GET /api/dashboard/kpi/` - KPI dashboard data
- `GET /api/operators/` - Available operators
- `POST /api/dispatches/{id}/start_journey/` - Start dispatch
- `POST /api/dispatches/{id}/weigh_in/` - Weigh-in process
- `POST /api/dispatches/{id}/unload/` - Unload process
- `POST /api/dispatches/{id}/weigh_out/` - Weigh-out process
- `POST /api/dispatches/{id}/complete_job/` - Complete dispatch

## Workflow Process

### 1. Order Creation
- Admin creates order for customer
- System automatically assigns available truck
- Creates dispatch record

### 2. Dispatch Workflow
1. **Assigned** - Dispatch created, truck assigned
2. **In Transit** - Operator starts journey
3. **Weigh In** - Capture gross weight + media
4. **Unload** - Confirm unloading + media
5. **Weigh Out** - Capture tare weight + media
6. **Completed** - Job finished, truck returns to idle

### 3. Automatic Actions
- Order status updates based on dispatch progress
- Material stock reduction on completion
- Truck status management
- Exception logging

## Frontend Components

### Admin Dashboard
- **Overview Tab**: KPI metrics, charts, statistics
- **Trucks Tab**: Fleet management (add/edit/delete)
- **Customers Tab**: Customer management (add/edit/delete)
- **Orders Tab**: Order management (add/edit/delete)
- **Dispatches Tab**: Dispatch tracking and management
- **Materials Tab**: Inventory management

### Operator Dashboard
- **My Dispatches**: Assigned dispatches
- **Workflow Actions**: Step-by-step process execution
- **Image Upload**: Media capture for each step
- **Status Updates**: Real-time progress tracking

## Key Features

### Real-time Tracking
- Live dispatch status updates
- GPS tracking capabilities (ready for integration)
- Media capture at each workflow step

### Role-based Access
- **Admin**: Full system access, user management
- **Operator**: Dispatch execution, status updates

### Data Visualization
- KPI dashboard with charts
- Material stock monitoring
- Exception tracking and resolution

### File Management
- Image upload for dispatch steps
- Media categorization (weigh_in, unload, weigh_out, etc.)
- Cloud storage integration ready

## Database Configuration

### Production Database (Hostinger)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u755489336_mineflow',
        'USER': 'u755489336_sekamble',
        'PASSWORD': '!Chiku@2210',
        'HOST': '193.203.184.166',
        'PORT': '3306',
    }
}
```

## Installation & Setup

### Backend Setup
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_admin

# Start server
python manage.py runserver 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Default Admin Credentials
- **Username**: admin
- **Email**: admin@mining.com
- **Password**: admin123

## API Authentication

All API endpoints (except login/register) require JWT authentication:
```javascript
headers: {
  'Authorization': 'Bearer <access_token>',
  'Content-Type': 'application/json'
}
```

## CORS Configuration

Frontend runs on `http://localhost:3000`
Backend runs on `http://localhost:8000`
CORS is configured to allow frontend-backend communication.

## File Upload

Media files are stored in `/media/dispatch_media/YYYY/MM/DD/`
Supported formats: Images (jpg, png, gif, etc.)

## Error Handling

- Comprehensive error logging
- User-friendly error messages
- Exception tracking system
- Automatic retry mechanisms

## Security Features

- JWT token-based authentication
- Role-based permissions
- CORS protection
- Input validation and sanitization
- SQL injection prevention

## Scalability Considerations

- Modular architecture
- RESTful API design
- Database indexing
- Caching ready
- Microservices migration path

## Future Enhancements

- Real-time notifications
- Mobile app integration
- Advanced analytics
- GPS tracking integration
- Automated reporting
- Multi-tenant support

## Development Commands

### Django Management Commands
```bash
# Create admin user
python manage.py create_admin

# Clear database
python manage.py clear_database --confirm

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

### Frontend Commands
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Troubleshooting

### Common Issues
1. **Django server not starting**: Ensure virtual environment is activated
2. **CORS errors**: Check CORS_ALLOWED_ORIGINS in settings.py
3. **Database connection**: Verify database credentials
4. **Frontend not loading**: Ensure backend is running on port 8000

### Logs Location
- Django logs: Console output
- Frontend logs: Browser console
- Error tracking: ExceptionLog model in database

## Contact & Support

For technical support or questions about this system, refer to the codebase documentation or contact the development team.

---

**Last Updated**: September 22, 2025
**Version**: 1.0.0
**Status**: Production Ready
