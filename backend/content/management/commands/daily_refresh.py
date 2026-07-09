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
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import FeedSource, Article
from content.management.commands.import_rss import import_feed

logger = logging.getLogger(__name__)

LOCK_FILE = os.path.join(tempfile.gettempdir(), "factly_daily_refresh.lock")

CUTOFF_HOURS = 24
TRENDING_LIMIT = 10


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

        # ------------------------------------------------------------------
        # Lock file — prevent concurrent runs
        # ------------------------------------------------------------------
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
            self._refresh(dry_run)
        finally:
            if not dry_run and os.path.exists(LOCK_FILE):
                try:
                    os.remove(LOCK_FILE)
                except OSError:
                    pass

    # ==================================================================
    # Internal helpers
    # ==================================================================

    def _refresh(self, dry_run):
        active = FeedSource.objects.filter(is_active=True)
        if not active.exists():
            self.stdout.write(self.style.WARNING(
                "No active feed sources found. Nothing to do."
            ))
            return

        cutoff = timezone.now() - timedelta(hours=CUTOFF_HOURS)

        # ------------------------------------------------------------------
        # Phase 1 — Import
        # ------------------------------------------------------------------
        self.stdout.write("=" * 60)
        self.stdout.write("PHASE 1: IMPORT  —  Fetching articles from all sources")
        self.stdout.write("=" * 60)

        total_imported = 0
        source_log = []

        for source in active:
            label = f"  {source.name}  ({source.feed_url})"
            self.stdout.write(label)

            if dry_run:
                self.stdout.write("    [DRY-RUN]  skipped (no changes made)")
                continue

            try:
                count = import_feed(source)
                total_imported += count
                source_log.append({"source": source.name, "imported": count})
                self.stdout.write(f"    imported {count} new article(s)")
            except Exception as exc:
                logger.exception("Import failed for %s", source.name)
                source_log.append({"source": source.name, "error": str(exc)})
                self.stdout.write(self.style.ERROR(f"    FAILED — {exc}"))

        # ------------------------------------------------------------------
        # Phase 2 — Rotate (only if at least one new article arrived)
        # ------------------------------------------------------------------
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("PHASE 2: ROTATE  —  Cycling out stale imported content")
        self.stdout.write("=" * 60)

        existing_count = Article.objects.filter(
            is_imported=True, deleted_at__isnull=True
        ).count()

        stale = Article.objects.filter(
            is_imported=True,
            deleted_at__isnull=True,
            published_at__lt=cutoff,
        )
        stale_count = stale.count()

        if dry_run:
            self.stdout.write(f"  existing imported articles:  {existing_count}")
            self.stdout.write(f"  would soft-delete (>{CUTOFF_HOURS}h old):  {stale_count}")
            self.stdout.write(f"  would NOT rotate (editorial content):  "
                             f"{Article.objects.filter(is_imported=False, deleted_at__isnull=True).count()}")
            self._print_dry_run_summary(active.count())
            return

        if total_imported == 0:
            self.stdout.write(self.style.WARNING(
                "No new articles were imported.  "
                "Skipping rotation to preserve existing content."
            ))
            self._print_summary(source_log, stale_count=0, fresh_count=0)
            return

        if stale_count:
            for article in stale.iterator(chunk_size=200):
                article.soft_delete()
            self.stdout.write(f"  soft-deleted {stale_count} imported article(s)")
        else:
            self.stdout.write("  no stale imported articles to rotate")

        # ------------------------------------------------------------------
        # Phase 3 — Promote trending
        # ------------------------------------------------------------------
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("PHASE 3: PROMOTE  —  Flagging freshest articles as trending")
        self.stdout.write("=" * 60)

        fresh = Article.objects.filter(
            is_imported=True,
            deleted_at__isnull=True,
            published_at__gte=cutoff,
        )
        fresh_count = fresh.count()

        if fresh_count:
            Article.objects.filter(is_imported=True).update(is_trending=False)

            trending = fresh.order_by("-published_at")[:TRENDING_LIMIT]
            for article in trending:
                article.is_trending = True
                article.save(update_fields=["is_trending"])

            self.stdout.write(
                f"  reset trending on all imported articles\n"
                f"  marked {len(trending)} freshest article(s) as trending"
            )
        else:
            self.stdout.write("  no fresh articles to promote")

        self._print_summary(source_log, stale_count, fresh_count)

    # ==================================================================
    # Reporting
    # ==================================================================

    def _print_summary(self, source_log, stale_count, fresh_count):
        total = sum(item.get("imported", 0) for item in source_log)
        errors = [item for item in source_log if "error" in item]

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("DAILY REFRESH  —  Complete")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  sources processed:          {len(source_log)}")
        self.stdout.write(f"  new articles imported:      {total}")
        self.stdout.write(f"  stale articles rotated:     {stale_count}")
        self.stdout.write(f"  fresh articles promoted:    {min(fresh_count, TRENDING_LIMIT) if fresh_count else 0}")

        if errors:
            self.stdout.write(self.style.WARNING(
                f"  sources with errors:        {len(errors)}"
            ))
            for err in errors:
                self.stdout.write(f"    - {err['source']}: {err['error']}")

    def _print_dry_run_summary(self, source_count):
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("DRY RUN  —  No data was modified")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  active feed sources:        {source_count}")
