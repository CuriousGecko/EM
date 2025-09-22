from access.api.models import AccessRole, AccessRule, BusinessElement
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Наполняет БД тестовыми данными.'

    def handle(self, *args, **options):
        admin_role = AccessRole.objects.create(name='admin')
        user_role = AccessRole.objects.create(name='user')
        guest_role = AccessRole.objects.create(name='guest')

        users_element = BusinessElement.objects.create(name='user')

        User.objects.create_user(
            email='admin@example.com',
            password='adminpass',
            first_name='Admin',
            last_name='Super',
            patronymic='',
            role=admin_role
        )

        User.objects.create_user(
            email='user@example.com',
            password='userpass',
            first_name='Normal',
            last_name='User',
            patronymic='',
            role=user_role
        )

        AccessRule.objects.get_or_create(
            role=admin_role,
            element=users_element,
            can_read_own=True,
            can_read_all=True,
            can_create=True,
            can_update_own=True,
            can_update_all=True,
            can_delete_own=True,
            can_delete_all=True
        )

        AccessRule.objects.get_or_create(
            role=user_role,
            element=users_element,
            can_read_own=True,
            can_read_all=True,
            can_create=False,
            can_update_own=True,
            can_update_all=False,
            can_delete_own=True,
            can_delete_all=False
        )

        AccessRule.objects.get_or_create(
            role=guest_role,
            element=users_element,
            can_read_own=False,
            can_read_all=False,
            can_create=True,
            can_update_own=False,
            can_update_all=False,
            can_delete_own=False,
            can_delete_all=False
        )

        self.stdout.write(self.style.SUCCESS('Фикстуры созданы!'))
