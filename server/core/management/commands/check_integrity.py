from core.healthcheck import ERROR, INTEGRATION_MODULE_MAP, OK
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """ Django command to check DB integrity """

    help = 'python manage.py check_integrity'

    def handle(self, *args, **options):
        has_errors = False
        for key, module in INTEGRATION_MODULE_MAP.items():
            integrity_check = module()
            integrity_check.run()

            self.stdout.write(f'...\tchecking {key}')
            if integrity_check.messages:
                for message in integrity_check.messages:
                    self.stdout.write(self.style.WARNING(message))

            if integrity_check.status == OK:
                self.stdout.write(self.style.SUCCESS(f'[{OK}]\t{key}'))
            else:
                self.stdout.write(self.style.ERROR(f'[{ERROR}]\t{key}'))
                self.stderr.write(
                    self.style.ERROR(f'{"".join(integrity_check.errors)}'))
                has_errors = True

        if not has_errors:
            self.stdout.write(
                self.style.SUCCESS(f'\n[{OK}]\tSYSTEM INTEGRITY STATUS'))
        else:
            raise CommandError('System integrity checks failed')
