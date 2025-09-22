from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import UserProfile, Truck, Customer, Order, Dispatch, Material, ExceptionLog, DispatchMedia
from .serializers import (
    UserSerializer, UserRegistrationSerializer, TruckSerializer, CustomerSerializer,
    OrderSerializer, MaterialSerializer, DispatchSerializer, ExceptionLogSerializer,
    KPIDashboardSerializer, OperatorSerializer, WorkflowStepSerializer, DispatchMediaSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user_data = serializer.validated_data
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=user_data.get('role', 'operator')
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            },
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh)
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

# Custom Permissions
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin'

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin'

class IsOperatorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if hasattr(request.user, 'userprofile'):
            return request.user.userprofile.role in ['admin', 'operator']
        return False

# ViewSets
class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Truck.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Customer.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(contact__icontains=search)
            )
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer').all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Order.objects.select_related('customer').all()
        status_filter = self.request.query_params.get('status', None)
        customer_filter = self.request.query_params.get('customer', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if customer_filter:
            queryset = queryset.filter(customer_id=customer_filter)
        return queryset

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Material.objects.all()
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock == 'true':
            queryset = queryset.filter(stock_quantity__lt=10)  # Assuming 10 is low stock threshold
        return queryset

class DispatchViewSet(viewsets.ModelViewSet):
    queryset = Dispatch.objects.select_related('truck', 'order', 'operator').prefetch_related('media_files').all()
    serializer_class = DispatchSerializer
    permission_classes = [IsAuthenticated, IsOperatorOrAdmin]

    def get_queryset(self):
        queryset = Dispatch.objects.select_related('truck', 'order', 'operator').prefetch_related('media_files').all()
        
        # Filter by operator if user is operator
        if hasattr(self.request.user, 'userprofile') and self.request.user.userprofile.role == 'operator':
            queryset = queryset.filter(operator=self.request.user)
        
        status_filter = self.request.query_params.get('status', None)
        operator_filter = self.request.query_params.get('operator', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if operator_filter:
            queryset = queryset.filter(operator_id=operator_filter)
            
        return queryset

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        dispatch = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['assigned', 'in_transit', 'weigh_in', 'unload', 'weigh_out', 'completed', 'cancelled']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        dispatch.status = new_status
        
        if new_status == 'in_transit' and not dispatch.departure_time:
            dispatch.departure_time = timezone.now()
        elif new_status == 'completed' and not dispatch.arrival_time:
            dispatch.arrival_time = timezone.now()
            
        dispatch.save()
        
        # Update related order status
        if new_status == 'completed':
            dispatch.order.status = 'completed'
            dispatch.order.save()
        elif new_status == 'in_transit':
            dispatch.order.status = 'in_progress'
            dispatch.order.save()
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_operator(self, request, pk=None):
        dispatch = self.get_object()
        operator_id = request.data.get('operator_id')
        
        if not operator_id:
            return Response({'error': 'Operator ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            operator = User.objects.get(id=operator_id)
            if not hasattr(operator, 'userprofile') or operator.userprofile.role != 'operator':
                return Response({'error': 'Invalid operator'}, status=status.HTTP_400_BAD_REQUEST)
            
            dispatch.operator = operator
            dispatch.save()
            
            serializer = self.get_serializer(dispatch)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'Operator not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def start_journey(self, request, pk=None):
        """Start Journey → mark dispatch as "In Transit"."""
        dispatch = self.get_object()
        
        if dispatch.status != 'assigned':
            return Response({'error': 'Dispatch must be assigned to start journey'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        dispatch.status = 'in_transit'
        dispatch.start_journey_time = timezone.now()
        dispatch.save()
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def weigh_in(self, request, pk=None):
        """Weigh-in → operator captures gross weight (optionally uploads slip/photo)."""
        dispatch = self.get_object()
        
        if dispatch.status != 'in_transit':
            return Response({'error': 'Dispatch must be in transit to weigh in'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        gross_weight = request.data.get('gross_weight')
        media_data = request.data.get('media', '')
        
        if not gross_weight:
            return Response({'error': 'Gross weight is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        dispatch.status = 'weigh_in'
        dispatch.weigh_in_time = timezone.now()
        dispatch.gross_weight = float(gross_weight)
        dispatch.weigh_in_media = media_data
        dispatch.save()
        
        # Handle image uploads
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                DispatchMedia.objects.create(
                    dispatch=dispatch,
                    media_type='weigh_in',
                    image=image,
                    uploaded_by=request.user,
                    description=request.data.get('description', '')
                )
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unload(self, request, pk=None):
        """Unload → operator confirms unloading (with media capture if needed)."""
        dispatch = self.get_object()
        
        if dispatch.status != 'weigh_in':
            return Response({'error': 'Dispatch must be weighed in to unload'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        media_data = request.data.get('media', '')
        
        dispatch.status = 'unload'
        dispatch.unload_time = timezone.now()
        dispatch.unload_media = media_data
        dispatch.save()
        
        # Handle image uploads
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                DispatchMedia.objects.create(
                    dispatch=dispatch,
                    media_type='unload',
                    image=image,
                    uploaded_by=request.user,
                    description=request.data.get('description', '')
                )
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def weigh_out(self, request, pk=None):
        """Weigh-out → operator records tare weight."""
        dispatch = self.get_object()
        
        if dispatch.status != 'unload':
            return Response({'error': 'Dispatch must be unloaded to weigh out'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        tare_weight = request.data.get('tare_weight')
        media_data = request.data.get('media', '')
        
        if not tare_weight:
            return Response({'error': 'Tare weight is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        dispatch.status = 'weigh_out'
        dispatch.weigh_out_time = timezone.now()
        dispatch.tare_weight = float(tare_weight)
        dispatch.weigh_out_media = media_data
        dispatch.save()
        
        # Handle image uploads
        if 'images' in request.FILES:
            for image in request.FILES.getlist('images'):
                DispatchMedia.objects.create(
                    dispatch=dispatch,
                    media_type='weigh_out',
                    image=image,
                    uploaded_by=request.user,
                    description=request.data.get('description', '')
                )
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete_job(self, request, pk=None):
        """Complete Job → system marks dispatch as "Completed"."""
        dispatch = self.get_object()
        
        if dispatch.status != 'weigh_out':
            return Response({'error': 'Dispatch must be weighed out to complete'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        dispatch.status = 'completed'
        dispatch.completion_time = timezone.now()
        dispatch.arrival_time = timezone.now()
        dispatch.save()
        
        # Update related order status
        dispatch.order.status = 'completed'
        dispatch.order.save()
        
        # Update material stock (reduce by order quantity)
        try:
            material = Material.objects.get(name=dispatch.order.material_type)
            material.stock_quantity -= dispatch.order.quantity
            if material.stock_quantity < 0:
                material.stock_quantity = 0  # Prevent negative stock
            material.save()
        except Material.DoesNotExist:
            # Create material if it doesn't exist
            Material.objects.create(
                name=dispatch.order.material_type,
                stock_quantity=0,
                unit='tons'
            )
        
        # Return truck to idle
        truck = dispatch.truck
        truck.status = 'idle'
        truck.save()
        
        serializer = self.get_serializer(dispatch)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """Upload images for a dispatch"""
        dispatch = self.get_object()
        media_type = request.data.get('media_type', 'other')
        description = request.data.get('description', '')
        
        if 'images' not in request.FILES:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for image in request.FILES.getlist('images'):
            media_obj = DispatchMedia.objects.create(
                dispatch=dispatch,
                media_type=media_type,
                image=image,
                uploaded_by=request.user,
                description=description
            )
            serializer = DispatchMediaSerializer(media_obj, context={'request': request})
            uploaded_images.append(serializer.data)
        
        return Response({
            'message': f'{len(uploaded_images)} images uploaded successfully',
            'images': uploaded_images
        }, status=status.HTTP_201_CREATED)

class DispatchMediaViewSet(viewsets.ModelViewSet):
    queryset = DispatchMedia.objects.select_related('dispatch', 'uploaded_by').all()
    serializer_class = DispatchMediaSerializer
    permission_classes = [IsAuthenticated, IsOperatorOrAdmin]

    def get_queryset(self):
        queryset = DispatchMedia.objects.select_related('dispatch', 'uploaded_by').all()
        
        # Filter by dispatch if specified
        dispatch_id = self.request.query_params.get('dispatch', None)
        if dispatch_id:
            queryset = queryset.filter(dispatch_id=dispatch_id)
        
        # Filter by media type if specified
        media_type = self.request.query_params.get('media_type', None)
        if media_type:
            queryset = queryset.filter(media_type=media_type)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class ExceptionLogViewSet(viewsets.ModelViewSet):
    queryset = ExceptionLog.objects.select_related('dispatch', 'resolved_by').all()
    serializer_class = ExceptionLogSerializer
    permission_classes = [IsAuthenticated, IsOperatorOrAdmin]

    def get_queryset(self):
        queryset = ExceptionLog.objects.select_related('dispatch', 'resolved_by').all()
        
        resolved_filter = self.request.query_params.get('resolved', None)
        dispatch_filter = self.request.query_params.get('dispatch', None)
        
        if resolved_filter is not None:
            resolved_bool = resolved_filter.lower() == 'true'
            queryset = queryset.filter(resolved=resolved_bool)
        if dispatch_filter:
            queryset = queryset.filter(dispatch_id=dispatch_filter)
            
        return queryset

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        exception = self.get_object()
        exception.resolved = True
        exception.resolved_by = request.user
        exception.resolved_at = timezone.now()
        exception.save()
        
        serializer = self.get_serializer(exception)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_operators(request):
    """Get list of all operators for assignment"""
    operators = User.objects.filter(userprofile__role='operator')
    serializer = OperatorSerializer(operators, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def kpi_dashboard(request):
    """Get KPI data for admin dashboard"""
    today = timezone.now().date()
    
    # Basic counts
    total_trucks = Truck.objects.count()
    active_dispatches = Dispatch.objects.filter(status__in=['assigned', 'in_progress']).count()
    completed_orders_today = Order.objects.filter(
        status='completed',
        updated_at__date=today
    ).count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_exceptions = ExceptionLog.objects.count()
    unresolved_exceptions = ExceptionLog.objects.filter(resolved=False).count()
    
    # Average delivery time calculation
    completed_dispatches = Dispatch.objects.filter(
        status='completed',
        departure_time__isnull=False,
        arrival_time__isnull=False
    )
    
    if completed_dispatches.exists():
        delivery_times = []
        for dispatch in completed_dispatches:
            if dispatch.departure_time and dispatch.arrival_time:
                delivery_time = (dispatch.arrival_time - dispatch.departure_time).total_seconds() / 3600  # hours
                delivery_times.append(delivery_time)
        
        average_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
    else:
        average_delivery_time = 0
    
    # Material stock summary
    materials = Material.objects.all()
    material_stock_summary = {
        material.name: {
            'quantity': material.stock_quantity,
            'unit': material.unit,
            'low_stock': material.stock_quantity < 10
        }
        for material in materials
    }
    
    kpi_data = {
        'total_trucks': total_trucks,
        'active_dispatches': active_dispatches,
        'completed_orders_today': completed_orders_today,
        'pending_orders': pending_orders,
        'total_exceptions': total_exceptions,
        'unresolved_exceptions': unresolved_exceptions,
        'average_delivery_time': round(average_delivery_time, 2),
        'material_stock_summary': material_stock_summary
    }
    
    serializer = KPIDashboardSerializer(kpi_data)
    return Response(serializer.data)
