from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('operator', 'Operator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operator')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Truck(models.Model):
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('in_transit', 'In Transit'),
    ]
    
    number_plate = models.CharField(max_length=20, unique=True)
    capacity = models.FloatField(validators=[MinValueValidator(0.1)])
    driver_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.number_plate} - {self.driver_name}"

    class Meta:
        ordering = ['-created_at']

class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.contact})"

    class Meta:
        ordering = ['name']

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    material_type = models.CharField(max_length=50)
    quantity = models.FloatField(validators=[MinValueValidator(0.1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} ({self.quantity} {self.material_type})"

    class Meta:
        ordering = ['-created_at']

class Dispatch(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_transit', 'In Transit'),
        ('weigh_in', 'Weigh In'),
        ('unload', 'Unload'),
        ('weigh_out', 'Weigh Out'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='dispatches')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='dispatches')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                limit_choices_to={'userprofile__role': 'operator'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    
    # Workflow tracking fields
    start_journey_time = models.DateTimeField(null=True, blank=True)
    weigh_in_time = models.DateTimeField(null=True, blank=True)
    gross_weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    weigh_in_media = models.TextField(blank=True, null=True)  # Store file paths or URLs
    unload_time = models.DateTimeField(null=True, blank=True)
    unload_media = models.TextField(blank=True, null=True)  # Store file paths or URLs
    weigh_out_time = models.DateTimeField(null=True, blank=True)
    tare_weight = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    weigh_out_media = models.TextField(blank=True, null=True)  # Store file paths or URLs
    completion_time = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dispatch #{self.id} - {self.truck.number_plate} for Order #{self.order.id}"

    class Meta:
        ordering = ['-created_at']

class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)
    stock_quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='tons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit})"

    class Meta:
        ordering = ['name']

class DispatchMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('weigh_in', 'Weigh In'),
        ('unload', 'Unload'),
        ('weigh_out', 'Weigh Out'),
        ('delivery_proof', 'Delivery Proof'),
        ('exception', 'Exception'),
        ('other', 'Other'),
    ]
    
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE, related_name='media_files')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='other')
    image = models.ImageField(upload_to='dispatch_media/%Y/%m/%d/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media #{self.id} - {self.dispatch.truck.number_plate} ({self.media_type})"

    class Meta:
        ordering = ['-created_at']

class ExceptionLog(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE, related_name='exceptions')
    description = models.TextField()
    exception_type = models.CharField(max_length=50, default='General')
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exception #{self.id} - {self.dispatch}"

    class Meta:
        ordering = ['-created_at']


# Signal handlers for automatic workflow
@receiver(post_save, sender=Dispatch)
def handle_dispatch_status_change(sender, instance, created, **kwargs):
    """Handle dispatch status changes and update related entities"""
    
    if not created:  # Only handle updates, not creation
        # When dispatch is completed, complete the order and update stock
        if instance.status == 'completed':
            # Complete the order
            order = instance.order
            if order.status != 'completed':
                order.status = 'completed'
                order.save()
                
                # Update material stock (reduce by order quantity)
                try:
                    material = Material.objects.get(name=order.material_type)
                    material.stock_quantity -= order.quantity
                    if material.stock_quantity < 0:
                        material.stock_quantity = 0  # Prevent negative stock
                    material.save()
                except Material.DoesNotExist:
                    # Create material if it doesn't exist
                    Material.objects.create(
                        name=order.material_type,
                        stock_quantity=0,
                        unit='tons'
                    )
            
            # Return truck to idle
            truck = instance.truck
            truck.status = 'idle'
            truck.save()
            
            # Set arrival time if not already set
            if not instance.arrival_time:
                instance.arrival_time = timezone.now()
                instance.save()
        
        # When dispatch starts (in_transit), update truck status and order status
        elif instance.status == 'in_transit':
            # Update truck status to in_transit
            truck = instance.truck
            truck.status = 'in_transit'
            truck.save()
            
            # Update order status to in_progress
            order = instance.order
            if order.status == 'pending':
                order.status = 'in_progress'
                order.save()
            
            # Set departure time if not already set
            if not instance.departure_time:
                instance.departure_time = timezone.now()
                instance.save()


@receiver(post_save, sender=Order)
def handle_order_creation(sender, instance, created, **kwargs):
    """Automatically assign truck and create dispatch when order is created"""
    
    if created and instance.status == 'pending':
        # Find an available truck (idle status)
        available_truck = Truck.objects.filter(status='idle').first()
        
        if available_truck:
            # Create dispatch automatically
            Dispatch.objects.create(
                truck=available_truck,
                order=instance,
                status='assigned'
            )


@receiver(post_delete, sender=Dispatch)
def handle_dispatch_deletion(sender, instance, **kwargs):
    """Return truck to idle when dispatch is deleted"""
    
    # Return truck to idle status
    truck = instance.truck
    truck.status = 'idle'
    truck.save()
    
    # Reset order status if it was in_progress
    order = instance.order
    if order.status == 'in_progress':
        order.status = 'pending'
        order.save()
