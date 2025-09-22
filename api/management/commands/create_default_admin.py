from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile

class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
            return

        # Create default admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@mineflow.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            is_staff=True,
            is_superuser=True
        )
        
        # Create admin profile
        UserProfile.objects.create(
            user=admin_user,
            role='admin'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user with username: {admin_user.username}')
        )
        self.stdout.write(
            self.style.SUCCESS('Default credentials:')
        )
        self.stdout.write(
            self.style.SUCCESS('Username: admin')
        )
        self.stdout.write(
            self.style.SUCCESS('Password: admin123')
        )
        self.stdout.write(
            self.style.SUCCESS('Email: admin@mineflow.com')
        )
