#!/usr/bin/env python
"""Test script to verify daily update tasks are working"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factly_backend.settings')
django.setup()

from services.tasks.refresh_tasks import (
    refresh_realtime_data,
    update_trending_topics,
    update_global_events,
    refresh_fact_check_cache
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("Testing Daily Update Tasks")
print("="*60)

results = {}

try:
    print("\n1. Refreshing real-time data...")
    result = refresh_realtime_data()
    print(f"   ✓ Real-time data refreshed")
    results['realtime_data'] = 'SUCCESS'
except Exception as e:
    print(f"   ✗ Error: {e}")
    results['realtime_data'] = f'ERROR: {str(e)}'

try:
    print("\n2. Updating trending topics...")
    result = update_trending_topics()
    print(f"   ✓ Trending topics updated")
    results['trending_topics'] = 'SUCCESS'
except Exception as e:
    print(f"   ✗ Error: {e}")
    results['trending_topics'] = f'ERROR: {str(e)}'

try:
    print("\n3. Updating global events...")
    result = update_global_events()
    print(f"   ✓ Global events updated")
    results['global_events'] = 'SUCCESS'
except Exception as e:
    print(f"   ✗ Error: {e}")
    results['global_events'] = f'ERROR: {str(e)}'

try:
    print("\n4. Refreshing fact-check cache...")
    result = refresh_fact_check_cache()
    print(f"   ✓ Fact-check cache refreshed")
    results['fact_check_cache'] = 'SUCCESS'
except Exception as e:
    print(f"   ✗ Error: {e}")
    results['fact_check_cache'] = f'ERROR: {str(e)}'

print("\n" + "="*60)
print("Daily Update Tests Complete!")
print("="*60)
print("\nSummary:")
for task, status in results.items():
    status_icon = "✓" if status == "SUCCESS" else "✗"
    print(f"  {status_icon} {task}: {status}")

print("\n" + "="*60)
print("Next: These tasks will run automatically on schedule:")
print("  • Real-time data: every 5 minutes")
print("  • Trending topics: every 15 minutes")
print("  • Global events: every 30 minutes")
print("  • Fact-check cache: every 24 hours (daily)")
print("="*60 + "\n")
