from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'trucks', views.TruckViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'dispatches', views.DispatchViewSet)
router.register(r'dispatch-media', views.DispatchMediaViewSet)
router.register(r'exceptions', views.ExceptionLogViewSet)

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    
    # KPI Dashboard
    path('dashboard/kpi/', views.kpi_dashboard, name='kpi_dashboard'),
    
    # Operators
    path('operators/', views.get_operators, name='get_operators'),
    
    # Include router URLs
    path('', include(router.urls)),
]
