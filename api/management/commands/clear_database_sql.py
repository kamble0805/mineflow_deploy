from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Clear all data from the database using raw SQL'

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

        with connection.cursor() as cursor:
            # Disable foreign key checks temporarily
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # Get all tables in the database
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            # Truncate each table
            for table in tables:
                table_name = table[0]
                if table_name.startswith('api_') or table_name in ['auth_user', 'auth_group', 'auth_permission', 'auth_user_groups', 'auth_user_user_permissions', 'django_admin_log', 'django_content_type', 'django_migrations', 'django_session']:
                    self.stdout.write(f'Truncating {table_name}...')
                    cursor.execute(f"TRUNCATE TABLE `{table_name}`;")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        self.stdout.write(
            self.style.SUCCESS('Successfully cleared all data from the database!')
        )
