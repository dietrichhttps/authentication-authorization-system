from django.core.management.base import BaseCommand
from permissions.models import Role, BusinessElement, AccessRoleRule
from users.models import User


class Command(BaseCommand):
    help = 'Загружает тестовые данные: роли, бизнес-элементы, правила доступа и пользователей'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаю загрузку тестовых данных...'))

        # Создание ролей
        self.stdout.write('Создание ролей...')
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={'description': 'Администратор системы с полными правами доступа'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана роль: {admin_role.name}'))
        else:
            self.stdout.write(f'  - Роль уже существует: {admin_role.name}')

        manager_role, created = Role.objects.get_or_create(
            name='manager',
            defaults={'description': 'Менеджер с расширенными правами доступа'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана роль: {manager_role.name}'))
        else:
            self.stdout.write(f'  - Роль уже существует: {manager_role.name}')

        user_role, created = Role.objects.get_or_create(
            name='user',
            defaults={'description': 'Обычный пользователь с базовыми правами'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана роль: {user_role.name}'))
        else:
            self.stdout.write(f'  - Роль уже существует: {user_role.name}')

        guest_role, created = Role.objects.get_or_create(
            name='guest',
            defaults={'description': 'Гость с ограниченными правами доступа'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создана роль: {guest_role.name}'))
        else:
            self.stdout.write(f'  - Роль уже существует: {guest_role.name}')

        # Создание бизнес-элементов
        self.stdout.write('Создание бизнес-элементов...')
        elements_data = [
            {'name': 'products', 'description': 'Продукты/Товары'},
            {'name': 'orders', 'description': 'Заказы'},
            {'name': 'shops', 'description': 'Магазины'},
            {'name': 'users', 'description': 'Пользователи'},
            {'name': 'access_rules', 'description': 'Правила доступа'},
        ]

        elements = {}
        for elem_data in elements_data:
            element, created = BusinessElement.objects.get_or_create(
                name=elem_data['name'],
                defaults={'description': elem_data['description']}
            )
            elements[elem_data['name']] = element
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создан элемент: {element.name}'))
            else:
                self.stdout.write(f'  - Элемент уже существует: {element.name}')

        # Создание правил доступа
        self.stdout.write('Создание правил доступа...')

        # Администратор - полный доступ ко всему
        for element_name, element in elements.items():
            rule, created = AccessRoleRule.objects.get_or_create(
                role=admin_role,
                element=element,
                defaults={
                    'read_permission': True,
                    'read_all_permission': True,
                    'create_permission': True,
                    'update_permission': True,
                    'update_all_permission': True,
                    'delete_permission': True,
                    'delete_all_permission': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создано правило: {admin_role.name} -> {element.name}'))

        # Менеджер - расширенные права
        manager_rules = {
            'products': {
                'read_all_permission': True,
                'create_permission': True,
                'update_all_permission': True,
                'delete_all_permission': True,
            },
            'orders': {
                'read_all_permission': True,
                'create_permission': True,
                'update_all_permission': True,
            },
            'shops': {
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
            },
        }

        for element_name, permissions in manager_rules.items():
            rule, created = AccessRoleRule.objects.get_or_create(
                role=manager_role,
                element=elements[element_name],
                defaults=permissions
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создано правило: {manager_role.name} -> {element_name}'))

        # Обычный пользователь - базовые права (только свои объекты)
        user_rules = {
            'products': {
                'read_permission': True,
                'create_permission': True,
                'update_permission': True,
                'delete_permission': True,
            },
            'orders': {
                'read_permission': True,
                'create_permission': True,
                'update_permission': True,
            },
            'shops': {
                'read_permission': True,
            },
        }

        for element_name, permissions in user_rules.items():
            rule, created = AccessRoleRule.objects.get_or_create(
                role=user_role,
                element=elements[element_name],
                defaults=permissions
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создано правило: {user_role.name} -> {element_name}'))

        # Гость - только чтение
        guest_rules = {
            'products': {
                'read_all_permission': True,
            },
            'shops': {
                'read_all_permission': True,
            },
        }

        for element_name, permissions in guest_rules.items():
            rule, created = AccessRoleRule.objects.get_or_create(
                role=guest_role,
                element=elements[element_name],
                defaults=permissions
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создано правило: {guest_role.name} -> {element_name}'))

        # Создание тестовых пользователей
        self.stdout.write('Создание тестовых пользователей...')

        test_users = [
            {
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'role': admin_role,
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'email': 'manager@example.com',
                'password': 'manager123',
                'first_name': 'Иван',
                'last_name': 'Менеджеров',
                'role': manager_role,
            },
            {
                'email': 'user@example.com',
                'password': 'user123',
                'first_name': 'Петр',
                'last_name': 'Пользователь',
                'role': user_role,
            },
            {
                'email': 'guest@example.com',
                'password': 'guest123',
                'first_name': 'Гость',
                'last_name': 'Гостевой',
                'role': guest_role,
            },
        ]

        for user_data in test_users:
            email = user_data.pop('email')
            password = user_data.pop('password')
            role = user_data.pop('role')
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data
            )
            
            if created:
                user.set_password(password)
                user.role = role
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Создан пользователь: {user.email} (роль: {role.name})'))
            else:
                # Обновляем пароль и роль, если пользователь уже существует
                user.set_password(password)
                user.role = role
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.save()
                self.stdout.write(f'  - Пользователь уже существует: {user.email} (обновлен)')

        self.stdout.write(self.style.SUCCESS('\n✓ Тестовые данные успешно загружены!'))
        self.stdout.write(self.style.SUCCESS('\nТестовые пользователи:'))
        self.stdout.write('  - admin@example.com / admin123 (Администратор)')
        self.stdout.write('  - manager@example.com / manager123 (Менеджер)')
        self.stdout.write('  - user@example.com / user123 (Пользователь)')
        self.stdout.write('  - guest@example.com / guest123 (Гость)')

