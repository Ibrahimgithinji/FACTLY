"""
Daily content refresh command.

Orchestrates a once-per-day content refresh pipeline:
   1. Import fresh articles from all active FeedSource entries
   2. Soft-delete imported articles older than 24 hours
   3. Promote the freshest imported articles as trending
   4. Log full statistics for auditability

Security & credibility
----------------------
  - All imported HTML is sanitised via bleach with a strict allowlist of
    tags, attributes, and styles (see import_rss.clean_html).
  - Only pre-configured FeedSource entries are consulted — no arbitrary or
    user-supplied URLs are ever fetched.
  - Source attribution (source_url, source_name) is preserved on every
    imported article so readers can trace the original material.
  - Soft-delete (deleted_at) is used instead of hard deletion so content
    can be restored if an import introduces bad data.
  - A lock file prevents concurrent runs, which matters when the command
    is triggered by cron / Windows Task Scheduler and a previous run may
    still be executing.
  - The ``--dry-run`` flag lets administrators preview every action before
    any data is changed.

Usage
-----
    python manage.py daily_refresh
    python manage.py daily_refresh --dry-run

Typical cron schedule (once per day at 06:00):
    0 6 * * * cd /path/to/backend && python manage.py daily_refresh

Typical Windows Task Scheduler:
    Action:   Start a program
    Program:  python
    Args:     manage.py daily_refresh
    Start in: C:/.../backend
    Trigger:  Daily at 06:00
"""

import os
import sys
import logging
import tempfile

from django.core.management.base import BaseCommand

from services.daily_refresh_service import run_daily_refresh

logger = logging.getLogger(__name__)

LOCK_FILE = os.path.join(tempfile.gettempdir(), "factly_daily_refresh.lock")


class Command(BaseCommand):
    help = (
        "Import articles from all active FeedSource entries, "
        "rotate out imported content older than 24 hours, "
        "and promote the freshest batch as trending."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the refresh without modifying any data.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        if os.path.exists(LOCK_FILE):
            self.stdout.write(self.style.ERROR(
                f"Lock file exists at {LOCK_FILE} — "
                "another daily_refresh may be running. "
                "Delete the file manually if the process is stuck."
            ))
            sys.exit(1)

        if not dry_run:
            try:
                with open(LOCK_FILE, "w") as f:
                    f.write(str(os.getpid()))
            except OSError as exc:
                self.stdout.write(self.style.WARNING(
                    f"Could not write lock file: {exc}"
                ))

        try:
            stats = run_daily_refresh(dry_run=dry_run)
            self._print_summary(stats)
        finally:
            if not dry_run and os.path.exists(LOCK_FILE):
                try:
                    os.remove(LOCK_FILE)
                except OSError:
                    pass

    def _print_summary(self, stats):
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("DAILY REFRESH  —  Complete")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  sources processed:          {stats['sources_processed']}")
        self.stdout.write(f"  new articles imported:      {stats['imported']}")
        self.stdout.write(f"  stale articles rotated:     {stats['rotated']}")
        self.stdout.write(f"  fresh articles promoted:    {stats['promoted']}")

        if stats['errors']:
            self.stdout.write(self.style.WARNING(
                f"  sources with errors:        {len(stats['errors'])}"
            ))
            for err in stats['errors']:
                self.stdout.write(f"    - {err['source']}: {err['error']}")
