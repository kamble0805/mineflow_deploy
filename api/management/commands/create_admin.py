from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile


class Command(BaseCommand):
    help = 'Create a superuser admin account'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )
            return

        # Create superuser
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@mining.com',
            password='admin123'
        )

        # Create UserProfile for the admin
        UserProfile.objects.create(
            user=admin_user,
            role='admin'
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created admin superuser!\n'
                'Username: admin\n'
                'Email: admin@mining.com\n'
                'Password: admin123'
            )
        )
