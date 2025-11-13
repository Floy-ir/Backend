import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Provision dedicated Celery crawler containers for specific routes using docker compose. "
        "Two workers are created per invocation: one for days 0-3 and one for days 4-14."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--route",
            action="append",
            dest="routes",
            required=True,
            help="Route to crawl in ORIGIN:DEST format. Provide multiple times for multiple routes.",
        )
        parser.add_argument(
            "--three-interval",
            type=int,
            default=10,
            help="Interval in minutes for the 0-3 day worker (default: 10).",
        )
        parser.add_argument(
            "--four-interval",
            type=int,
            default=20,
            help="Interval in minutes for the 4-14 day worker (default: 20).",
        )
        parser.add_argument(
            "--three-offset",
            type=int,
            default=0,
            help="Minute offset (0-59) for the 0-3 day worker cron schedule (default: 0).",
        )
        parser.add_argument(
            "--four-offset",
            type=int,
            default=5,
            help="Minute offset (0-59) for the 4-14 day worker cron schedule (default: 5).",
        )
        parser.add_argument(
            "--project-name",
            type=str,
            default=None,
            help="Docker compose project name. Defaults to route-crawler-<slug>.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Output the generated compose file and command without executing docker compose.",
        )
        parser.add_argument(
            "--keep-config",
            action="store_true",
            help="Keep the generated override compose file instead of deleting it after execution.",
        )

    def handle(self, *args, **options):
        docker_binary = shutil.which("docker")
        if not docker_binary:
            raise CommandError("'docker' executable not found on PATH. Please install Docker.")

        routes = self._parse_routes(options["routes"] or [])
        routes_env = ",".join(f"{origin}:{destination}" for origin, destination in routes)

        three_interval = self._validate_interval(options["three_interval"], "three-interval")
        four_interval = self._validate_interval(options["four_interval"], "four-interval")
        three_offset = self._validate_offset(options["three_offset"], "three-offset")
        four_offset = self._validate_offset(options["four_offset"], "four-offset")

        slug = self._build_slug(routes)
        project_name = options["project_name"] or f"route-crawler-{slug}"

        service_three = f"crawler-three-{slug}"
        service_four = f"crawler-four-{slug}"
        container_three = f"{project_name}-three"
        container_four = f"{project_name}-four"
        volume_three = f"{project_name.replace('-', '_')}_beat_three"
        volume_four = f"{project_name.replace('-', '_')}_beat_four"

        override_content = self._build_override_content(
            service_three=service_three,
            service_four=service_four,
            container_three=container_three,
            container_four=container_four,
            volume_three=volume_three,
            volume_four=volume_four,
            routes_env=routes_env,
            three_interval=three_interval,
            four_interval=four_interval,
            three_offset=three_offset,
            four_offset=four_offset,
        )

        base_compose = Path(settings.BASE_DIR) / "docker-compose.yml"
        if not base_compose.exists():
            raise CommandError(f"Base docker-compose.yml not found at {base_compose}.")

        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(override_content)

        command = [
            docker_binary,
            "compose",
            "-f",
            str(base_compose),
            "-f",
            str(tmp_path),
            "--project-name",
            project_name,
            "up",
            "-d",
            service_three,
            service_four,
        ]

        if options["dry_run"]:
            self.stdout.write(self.style.NOTICE("Dry run requested. No containers created."))
            self.stdout.write("Generated override compose file:\n" + override_content)
            self.stdout.write("Command:")
            self.stdout.write(" ".join(command))
            if not options["keep_config"]:
                tmp_path.unlink(missing_ok=True)
            return

        try:
            subprocess.run(command, cwd=str(base_compose.parent), check=True)
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"docker compose execution failed: {exc}")
        finally:
            if not options["keep_config"]:
                tmp_path.unlink(missing_ok=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Launched crawler containers for routes {routes_env} (project: {project_name})."
            )
        )

    def _parse_routes(self, raw_routes: List[str]) -> List[Tuple[str, str]]:
        if not raw_routes:
            raise CommandError("At least one --route must be provided.")

        parsed: List[Tuple[str, str]] = []
        for value in raw_routes:
            parts = (value or "").split(":", 1)
            if len(parts) != 2:
                raise CommandError(f"Invalid route '{value}'. Expected format ORG:DST.")

            origin, destination = parts[0].strip().upper(), parts[1].strip().upper()
            if not origin or not destination:
                raise CommandError(f"Invalid route '{value}'. Origin and destination are required.")

            parsed.append((origin, destination))

        return parsed

    def _validate_interval(self, value: int, option: str) -> int:
        if value <= 0 or value > 60:
            raise CommandError(f"--{option} must be between 1 and 60 minutes.")
        return value

    def _validate_offset(self, value: int, option: str) -> int:
        if value < 0 or value > 59:
            raise CommandError(f"--{option} must be in the range 0-59.")
        return value

    def _build_slug(self, routes: List[Tuple[str, str]]) -> str:
        identifier = "-".join(f"{origin.lower()}-{destination.lower()}" for origin, destination in routes)
        identifier = identifier[:60]  # keep things manageable
        slug = re.sub(r"[^a-z0-9-]", "-", identifier)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug or "routes"

    def _build_override_content(
        self,
        *,
        service_three: str,
        service_four: str,
        container_three: str,
        container_four: str,
        volume_three: str,
        volume_four: str,
        routes_env: str,
        three_interval: int,
        four_interval: int,
        three_offset: int,
        four_offset: int,
    ) -> str:
        return (
            "services:\n"
            f"  {service_three}:\n"
            "    build:\n"
            "      context: .\n"
            "      dockerfile: Dockerfile\n"
            "    image: floy_backend:latest\n"
            f"    container_name: {container_three}\n"
            "    volumes:\n"
            "      - /etc/localtime:/etc/localtime:ro\n"
            "      - .:/app\n"
            f"      - {volume_three}:/app/celerybeat-data\n"
            "    entrypoint: celery -A runner.schedule.celery\n"
            "    command: worker --beat --loglevel=INFO --concurrency=1\n"
            "    env_file:\n"
            "      - .env\n"
            "    environment:\n"
            "      - BEAT_ROLE=three_days\n"
            "      - BEAT_SCHEDULE_FILE=/app/celerybeat-data/celerybeat-schedule\n"
            "      - C_FORCE_ROOT=true\n"
            "      - PYTHONUNBUFFERED=1\n"
            f"      - CRAWL_ROUTES={routes_env}\n"
            f"      - THREE_DAY_INTERVAL_MINUTES={three_interval}\n"
            f"      - THREE_DAY_OFFSET_MINUTE={three_offset}\n"
            "    networks:\n"
            "      - floy_network\n"
            "    depends_on:\n"
            "      db:\n"
            "        condition: service_healthy\n"
            "      redis:\n"
            "        condition: service_healthy\n"
            "      rabbitmq:\n"
            "        condition: service_healthy\n"
            f"  {service_four}:\n"
            "    build:\n"
            "      context: .\n"
            "      dockerfile: Dockerfile\n"
            "    image: floy_backend:latest\n"
            f"    container_name: {container_four}\n"
            "    volumes:\n"
            "      - /etc/localtime:/etc/localtime:ro\n"
            "      - .:/app\n"
            f"      - {volume_four}:/app/celerybeat-data\n"
            "    entrypoint: celery -A runner.schedule.celery\n"
            "    command: worker --beat --loglevel=INFO --concurrency=2 --max-tasks-per-child=1000 --max-memory-per-child=512000\n"
            "    env_file:\n"
            "      - .env\n"
            "    environment:\n"
            "      - BEAT_ROLE=four_plus\n"
            "      - BEAT_SCHEDULE_FILE=/app/celerybeat-data/celerybeat-schedule\n"
            "      - C_FORCE_ROOT=true\n"
            "      - PYTHONUNBUFFERED=1\n"
            f"      - CRAWL_ROUTES={routes_env}\n"
            f"      - FOUR_PLUS_INTERVAL_MINUTES={four_interval}\n"
            f"      - FOUR_PLUS_OFFSET_MINUTE={four_offset}\n"
            "    networks:\n"
            "      - floy_network\n"
            "    depends_on:\n"
            "      db:\n"
            "        condition: service_healthy\n"
            "      redis:\n"
            "        condition: service_healthy\n"
            "      rabbitmq:\n"
            "        condition: service_healthy\n"
            "volumes:\n"
            f"  {volume_three}:\n"
            f"  {volume_four}:\n"
        )

