from django.core.management.base import BaseCommand
from django.db import transaction

from apps.flight_crawler.models import Website, WebsiteRoute


class Command(BaseCommand):
    help = "Create WebsiteRoute entries for all active websites with origin 'thr' and destination 'AWZ' (is_supported=True)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing to the database.",
        )
        parser.add_argument(
            "--origin",
            default="thr",
            help="IATA origin code (default: thr)",
        )
        parser.add_argument(
            "--destination",
            default="AWZ",
            help="IATA destination code (default: AWZ)",
        )
        parser.add_argument(
            "--unsupported",
            action="store_true",
            help="Create routes with is_supported=False (default is True)",
        )

    def handle(self, *args, **options):
        origin = options["origin"].strip()
        destination = options["destination"].strip()
        is_supported = not options["unsupported"]
        dry_run = options["dry_run"]

        active_websites = Website.objects.filter(is_active=True)
        self.stdout.write(
            self.style.NOTICE(
                f"Processing {active_websites.count()} active website(s) for route {origin}  {destination} (is_supported={is_supported})"
            )
        )

        existing_website_ids = set(
            WebsiteRoute.objects.filter(
                origin=origin,
                destination=destination,
                is_supported=is_supported,
                website__in=active_websites,
            ).values_list("website_id", flat=True)
        )

        to_create = [
            WebsiteRoute(
                website=website,
                origin=origin,
                destination=destination,
                is_supported=is_supported,
            )
            for website in active_websites
            if website.id not in existing_website_ids
        ]

        if not to_create:
            self.stdout.write(self.style.SUCCESS("No routes to create. All up to date."))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Will create {len(to_create)} route(s): {origin}  {destination} (is_supported={is_supported})"
            )
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run enabled; no changes written."))
            return

        with transaction.atomic():
            # unique_together on (website, origin, destination) will prevent duplicates.
            # ignore_conflicts=True ensures concurrent duplicates won't error out (PostgreSQL).
            WebsiteRoute.objects.bulk_create(to_create, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(to_create)} route(s)."))
