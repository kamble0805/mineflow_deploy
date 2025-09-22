from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import (
    UserProfile, Truck, Customer, Order, Dispatch, 
    Material, DispatchMedia, ExceptionLog
)
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Clear all data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    'This will delete ALL data from the database!\n'
                    'Use --confirm flag to proceed.'
                )
            )
            return

        with transaction.atomic():
            # Delete in reverse order to respect foreign key constraints
            self.stdout.write('Deleting DispatchMedia...')
            DispatchMedia.objects.all().delete()
            
            self.stdout.write('Deleting ExceptionLog...')
            ExceptionLog.objects.all().delete()
            
            self.stdout.write('Deleting Dispatch...')
            Dispatch.objects.all().delete()
            
            self.stdout.write('Deleting Order...')
            Order.objects.all().delete()
            
            self.stdout.write('Deleting Customer...')
            Customer.objects.all().delete()
            
            self.stdout.write('Deleting Material...')
            Material.objects.all().delete()
            
            self.stdout.write('Deleting Truck...')
            Truck.objects.all().delete()
            
            self.stdout.write('Deleting UserProfile...')
            UserProfile.objects.all().delete()
            
            # Note: We're not deleting User objects as they might be needed for admin access
            # If you want to delete users too, uncomment the next line:
            # self.stdout.write('Deleting User...')
            # User.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all data from the database!')
        )
