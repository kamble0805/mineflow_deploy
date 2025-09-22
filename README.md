# MineFlow - Mining Operations Management System

A comprehensive mining operations management platform with role-based access control, dispatch management, and real-time monitoring capabilities.

## Features

### 🔐 Authentication & Authorization
- **User Authentication**: Login and signup functionality with JWT tokens
- **Role-based Access**: Admin and Operator roles with different permissions
- **Protected Routes**: Automatic redirection based on user roles
- **Secure API**: JWT-based authentication with token refresh

### 🚛 Core Operations Management
- **Truck Management**: Track fleet vehicles, drivers, and capacity
- **Order Management**: Handle customer orders and material requests
- **Dispatch System**: Assign and track dispatch operations
- **Material Inventory**: Monitor stock levels and material types
- **Exception Logging**: Track and resolve operational issues

### 📊 Analytics & Reporting
- **KPI Dashboard**: Real-time metrics and performance indicators
- **Interactive Charts**: Visual data representation with Recharts
- **Material Stock Monitoring**: Track inventory levels and alerts
- **Delivery Time Analytics**: Average delivery time calculations
- **Exception Tracking**: Monitor and resolve operational issues

### 👥 Role-based Features

#### Admin Dashboard
- **Full System Access**: Manage all entities (trucks, orders, dispatches, materials)
- **KPI Monitoring**: View comprehensive analytics and performance metrics
- **Dispatch Assignment**: Assign dispatches to operators
- **User Management**: Create and manage user accounts
- **Inventory Management**: Monitor and manage material stock levels

#### Operator Dashboard
- **Dispatch Management**: View and update assigned dispatch status
- **Exception Reporting**: Log operational issues and problems
- **Task Tracking**: Monitor assigned tasks and completion status
- **Real-time Updates**: Track dispatch progress and status changes

## Tech Stack

### Backend
- Django 5.2.6
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- MySQL Database
- CORS support

### Frontend
- React 18
- React Router DOM
- Axios for API calls
- Modern CSS with responsive design

## Setup Instructions

### Backend Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   - The project is configured to use MySQL
   - Update database settings in `backend/settings.py` if needed

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create Default Admin User**
   ```bash
   python manage.py create_default_admin
   ```

5. **Populate Sample Data (Optional)**
   ```bash
   python manage.py populate_sample_data
   ```

6. **Start Backend Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend Server**
   ```bash
   npm start
   ```

## Default Credentials

**Admin User:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@mineflow.com`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/refresh/` - Refresh access token

### Core Entities
- `GET/POST /api/trucks/` - List/Create trucks
- `GET/PUT/DELETE /api/trucks/{id}/` - Retrieve/Update/Delete truck
- `GET/POST /api/customers/` - List/Create customers
- `GET/PUT/DELETE /api/customers/{id}/` - Retrieve/Update/Delete customer
- `GET/POST /api/orders/` - List/Create orders
- `GET/PUT/DELETE /api/orders/{id}/` - Retrieve/Update/Delete order
- `GET/POST /api/materials/` - List/Create materials
- `GET/PUT/DELETE /api/materials/{id}/` - Retrieve/Update/Delete material

### Dispatch Management
- `GET/POST /api/dispatches/` - List/Create dispatches
- `GET/PUT/DELETE /api/dispatches/{id}/` - Retrieve/Update/Delete dispatch
- `POST /api/dispatches/{id}/update_status/` - Update dispatch status
- `POST /api/dispatches/{id}/assign_operator/` - Assign operator to dispatch

### Exception Logging
- `GET/POST /api/exceptions/` - List/Create exceptions
- `GET/PUT/DELETE /api/exceptions/{id}/` - Retrieve/Update/Delete exception
- `POST /api/exceptions/{id}/resolve/` - Resolve exception

### Analytics
- `GET /api/dashboard/kpi/` - Get KPI dashboard data

## User Roles

### Admin
- Full system access
- User management capabilities
- System settings and configuration
- Analytics and reporting
- Security management

### Operator
- Limited access to assigned operations
- Task management
- Equipment monitoring
- Report generation
- Activity logging

## Project Structure

```
mineflow/
├── backend/                 # Django backend
│   ├── settings.py         # Django settings
│   └── urls.py            # Main URL configuration
├── api/                   # API app
│   ├── models.py         # User and UserProfile models
│   ├── views.py          # Authentication views
│   ├── serializers.py    # API serializers
│   ├── urls.py           # API URL patterns
│   └── management/       # Custom management commands
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   ├── services/     # API services
│   │   └── App.js        # Main App component
└── README.md
```

## Usage

1. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/

2. **Login as Admin**
   - Use the default admin credentials to access the admin dashboard
   - Full system management capabilities

3. **Register as Operator**
   - Create a new operator account through the signup page
   - Access the operator dashboard with limited permissions

4. **Role-based Navigation**
   - Users are automatically redirected to appropriate dashboards based on their role
   - Protected routes prevent unauthorized access

## Security Features

- JWT token-based authentication
- Automatic token refresh
- Password validation
- CORS protection
- Role-based access control
- Secure logout with token blacklisting

## Development Notes

- The backend runs on port 8000
- The frontend runs on port 3000
- CORS is configured for development (should be restricted in production)
- JWT tokens expire after 1 day (access) and 7 days (refresh)

## Production Considerations

1. Update CORS settings in `backend/settings.py`
2. Use environment variables for sensitive settings
3. Enable HTTPS
4. Configure proper database settings
5. Set up proper logging and monitoring
6. Use a production WSGI server (e.g., Gunicorn)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
"# mineflow_deploy" 
