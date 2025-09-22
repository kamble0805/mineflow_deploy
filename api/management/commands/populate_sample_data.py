from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile, Truck, Customer, Order, Material, Dispatch

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        # Create sample materials
        materials = [
            {'name': 'Coal', 'stock_quantity': 500, 'unit': 'tons'},
            {'name': 'Iron Ore', 'stock_quantity': 300, 'unit': 'tons'},
            {'name': 'Sand', 'stock_quantity': 800, 'unit': 'tons'},
            {'name': 'Gravel', 'stock_quantity': 600, 'unit': 'tons'},
            {'name': 'Limestone', 'stock_quantity': 400, 'unit': 'tons'},
        ]
        
        for material_data in materials:
            material, created = Material.objects.get_or_create(
                name=material_data['name'],
                defaults=material_data
            )
            if created:
                self.stdout.write(f'Created material: {material.name}')

        # Create sample trucks
        trucks = [
            {'number_plate': 'ABC-123', 'capacity': 50.0, 'driver_name': 'John Smith', 'status': 'idle'},
            {'number_plate': 'XYZ-456', 'capacity': 45.0, 'driver_name': 'Jane Doe', 'status': 'idle'},
            {'number_plate': 'DEF-789', 'capacity': 55.0, 'driver_name': 'Mike Johnson', 'status': 'in_transit'},
            {'number_plate': 'GHI-012', 'capacity': 40.0, 'driver_name': 'Sarah Wilson', 'status': 'idle'},
            {'number_plate': 'JKL-345', 'capacity': 60.0, 'driver_name': 'Tom Brown', 'status': 'idle'},
        ]
        
        for truck_data in trucks:
            truck, created = Truck.objects.get_or_create(
                number_plate=truck_data['number_plate'],
                defaults=truck_data
            )
            if created:
                self.stdout.write(f'Created truck: {truck.number_plate}')

        # Create sample customers
        customers = [
            {'name': 'ABC Construction Ltd', 'contact': '+1234567890', 'email': 'contact@abcconstruction.com'},
            {'name': 'XYZ Mining Corp', 'contact': '+0987654321', 'email': 'orders@xyzmining.com'},
            {'name': 'DEF Industries', 'contact': '+1122334455', 'email': 'procurement@defindustries.com'},
            {'name': 'GHI Builders', 'contact': '+5566778899', 'email': 'supplies@ghibuilders.com'},
            {'name': 'JKL Contractors', 'contact': '+9988776655', 'email': 'orders@jklcontractors.com'},
        ]
        
        for customer_data in customers:
            customer, created = Customer.objects.get_or_create(
                name=customer_data['name'],
                defaults=customer_data
            )
            if created:
                self.stdout.write(f'Created customer: {customer.name}')

        # Create sample orders
        customers = Customer.objects.all()
        materials = Material.objects.all()
        
        orders = [
            {'customer': customers[0], 'material_type': 'Coal', 'quantity': 100.0, 'status': 'pending'},
            {'customer': customers[1], 'material_type': 'Iron Ore', 'quantity': 75.0, 'status': 'pending'},
            {'customer': customers[2], 'material_type': 'Sand', 'quantity': 150.0, 'status': 'in_progress'},
            {'customer': customers[3], 'material_type': 'Gravel', 'quantity': 200.0, 'status': 'completed'},
            {'customer': customers[4], 'material_type': 'Limestone', 'quantity': 80.0, 'status': 'pending'},
            {'customer': customers[0], 'material_type': 'Coal', 'quantity': 120.0, 'status': 'pending'},
        ]
        
        for order_data in orders:
            order, created = Order.objects.get_or_create(
                customer=order_data['customer'],
                material_type=order_data['material_type'],
                quantity=order_data['quantity'],
                defaults={'status': order_data['status']}
            )
            if created:
                self.stdout.write(f'Created order: Order #{order.id}')

        # Create sample dispatches
        trucks = Truck.objects.all()
        orders = Order.objects.all()
        operators = User.objects.filter(userprofile__role='operator')
        
        if operators.exists():
            dispatch_data = [
                {'truck': trucks[2], 'order': orders[2], 'operator': operators.first(), 'status': 'in_progress'},
                {'truck': trucks[0], 'order': orders[0], 'status': 'assigned'},
                {'truck': trucks[1], 'order': orders[1], 'status': 'assigned'},
            ]
            
            for dispatch_info in dispatch_data:
                dispatch, created = Dispatch.objects.get_or_create(
                    truck=dispatch_info['truck'],
                    order=dispatch_info['order'],
                    defaults={
                        'operator': dispatch_info.get('operator'),
                        'status': dispatch_info['status']
                    }
                )
                if created:
                    self.stdout.write(f'Created dispatch: Dispatch #{dispatch.id}')

        self.stdout.write(
            self.style.SUCCESS('Sample data populated successfully!')
        )
