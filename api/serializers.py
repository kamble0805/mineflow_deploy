from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from .models import UserProfile, Truck, Customer, Order, Dispatch, Material, ExceptionLog, DispatchMedia

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    role = serializers.CharField(source='userprofile.role', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='operator')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists")
        return value

class TruckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Truck
        fields = ['id', 'number_plate', 'capacity', 'driver_name', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'contact', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_contact = serializers.CharField(source='customer.contact', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'customer_name', 'customer_contact', 'material_type', 'quantity', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'stock_quantity', 'unit', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DispatchMediaSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DispatchMedia
        fields = ['id', 'dispatch', 'media_type', 'image', 'image_url', 'description', 
                 'uploaded_by', 'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}".strip() or obj.uploaded_by.username
        return None
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class DispatchSerializer(serializers.ModelSerializer):
    truck_number_plate = serializers.CharField(source='truck.number_plate', read_only=True)
    truck_driver = serializers.CharField(source='truck.driver_name', read_only=True)
    order_customer = serializers.CharField(source='order.customer.name', read_only=True)
    order_material = serializers.CharField(source='order.material_type', read_only=True)
    order_quantity = serializers.FloatField(source='order.quantity', read_only=True)
    operator_name = serializers.SerializerMethodField()
    media_files = DispatchMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dispatch
        fields = ['id', 'truck', 'truck_number_plate', 'truck_driver', 'order', 'order_customer', 
                 'order_material', 'order_quantity', 'operator', 'operator_name', 'status', 
                 'departure_time', 'arrival_time', 'start_journey_time', 'weigh_in_time', 
                 'gross_weight', 'weigh_in_media', 'unload_time', 'unload_media', 
                 'weigh_out_time', 'tare_weight', 'weigh_out_media', 'completion_time',
                 'media_files', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_operator_name(self, obj):
        if obj.operator:
            return f"{obj.operator.first_name} {obj.operator.last_name}".strip() or obj.operator.username
        return None

class ExceptionLogSerializer(serializers.ModelSerializer):
    dispatch_truck = serializers.CharField(source='dispatch.truck.number_plate', read_only=True)
    dispatch_order = serializers.CharField(source='dispatch.order.id', read_only=True)
    resolved_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ExceptionLog
        fields = ['id', 'dispatch', 'dispatch_truck', 'dispatch_order', 'description', 
                 'exception_type', 'resolved', 'resolved_by', 'resolved_by_name', 
                 'resolved_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    
    def get_resolved_by_name(self, obj):
        if obj.resolved_by:
            return f"{obj.resolved_by.first_name} {obj.resolved_by.last_name}".strip() or obj.resolved_by.username
        return None

class OperatorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class WorkflowStepSerializer(serializers.Serializer):
    step = serializers.CharField()
    data = serializers.DictField(required=False)

class KPIDashboardSerializer(serializers.Serializer):
    total_trucks = serializers.IntegerField()
    active_dispatches = serializers.IntegerField()
    completed_orders_today = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_exceptions = serializers.IntegerField()
    unresolved_exceptions = serializers.IntegerField()
    average_delivery_time = serializers.FloatField()
    material_stock_summary = serializers.DictField()
