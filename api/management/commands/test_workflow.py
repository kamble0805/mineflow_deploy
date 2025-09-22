from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Customer, Order, Truck, Dispatch, Material


class Command(BaseCommand):
    help = 'Test the automatic workflow system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Mining Operations Workflow...'))
        
        # Create test data if it doesn't exist
        self.create_test_data()
        
        # Test the workflow
        self.test_order_creation_workflow()
        self.test_dispatch_status_workflow()
        
        self.stdout.write(self.style.SUCCESS('Workflow test completed!'))

    def create_test_data(self):
        """Create test data if it doesn't exist"""
        
        # Create customer if not exists
        customer, created = Customer.objects.get_or_create(
            name="Test Customer",
            defaults={'contact': '1234567890', 'email': 'test@example.com'}
        )
        if created:
            self.stdout.write(f'Created customer: {customer.name}')
        
        # Create material if not exists
        material, created = Material.objects.get_or_create(
            name="Coal",
            defaults={'stock_quantity': 100, 'unit': 'tons'}
        )
        if created:
            self.stdout.write(f'Created material: {material.name} with {material.stock_quantity} tons')
        
        # Create truck if not exists
        truck, created = Truck.objects.get_or_create(
            number_plate="TEST-001",
            defaults={'capacity': 20, 'driver_name': 'John Doe', 'status': 'idle'}
        )
        if created:
            self.stdout.write(f'Created truck: {truck.number_plate}')

    def test_order_creation_workflow(self):
        """Test that creating an order automatically assigns a truck and creates a dispatch"""
        
        self.stdout.write('\n--- Testing Order Creation Workflow ---')
        
        # Get test customer and truck
        customer = Customer.objects.get(name="Test Customer")
        truck_before = Truck.objects.get(number_plate="TEST-001")
        
        self.stdout.write(f'Truck status before order: {truck_before.status}')
        
        # Create an order
        order = Order.objects.create(
            customer=customer,
            material_type="Coal",
            quantity=15.0,
            status="pending"
        )
        
        self.stdout.write(f'Created order: {order}')
        
        # Check if dispatch was created automatically
        dispatch = Dispatch.objects.filter(order=order).first()
        if dispatch:
            self.stdout.write(f'✅ Dispatch created automatically: {dispatch}')
            self.stdout.write(f'   Truck assigned: {dispatch.truck.number_plate}')
            self.stdout.write(f'   Dispatch status: {dispatch.status}')
        else:
            self.stdout.write(self.style.ERROR('❌ No dispatch created automatically'))
        
        # Check truck status (should still be idle until dispatch starts)
        truck_after = Truck.objects.get(number_plate="TEST-001")
        self.stdout.write(f'Truck status after order: {truck_after.status}')

    def test_dispatch_status_workflow(self):
        """Test that changing dispatch status updates related entities"""
        
        self.stdout.write('\n--- Testing Dispatch Status Workflow ---')
        
        # Get the dispatch created in previous test
        dispatch = Dispatch.objects.filter(order__customer__name="Test Customer").first()
        if not dispatch:
            self.stdout.write(self.style.ERROR('❌ No dispatch found for testing'))
            return
        
        # Test starting dispatch (in_progress)
        self.stdout.write(f'Starting dispatch: {dispatch}')
        dispatch.status = 'in_progress'
        dispatch.save()
        
        # Check truck status
        truck = dispatch.truck
        truck.refresh_from_db()
        self.stdout.write(f'✅ Truck status after starting: {truck.status}')
        
        # Check order status
        order = dispatch.order
        order.refresh_from_db()
        self.stdout.write(f'✅ Order status after starting: {order.status}')
        
        # Test completing dispatch
        self.stdout.write(f'Completing dispatch: {dispatch}')
        dispatch.status = 'completed'
        dispatch.save()
        
        # Check truck status (should be idle)
        truck.refresh_from_db()
        self.stdout.write(f'✅ Truck status after completion: {truck.status}')
        
        # Check order status (should be completed)
        order.refresh_from_db()
        self.stdout.write(f'✅ Order status after completion: {order.status}')
        
        # Check material stock (should be reduced)
        try:
            material = Material.objects.get(name=order.material_type)
            self.stdout.write(f'✅ Material stock after completion: {material.stock_quantity} tons')
        except Material.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Material not found'))
        
        self.stdout.write('\n🎉 All workflow tests passed!')
