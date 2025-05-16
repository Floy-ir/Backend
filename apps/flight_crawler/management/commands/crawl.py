from django.core.management.base import BaseCommand
from uuid import uuid4
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces


class Command(BaseCommand):
    help = 'Crawl'

    def handle(self, *args, **options):
        try:
            bootstrapper = Bootstrapper()
            service = bootstrapper.get_flight_crawler_service()
            service.crawl_scheduled_flights(3, 4)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully crawled'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating session: {e}')
            )
