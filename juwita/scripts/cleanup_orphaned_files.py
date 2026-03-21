#!/usr/bin/env python
"""
Cleanup script for orphaned meeting photos.
Removes uploaded files that are not connected to any meeting.

Usage:
    python manage.py shell < scripts/cleanup_orphaned_files.py

Or run directly:
    cd /home/juwita/juwita && source /home/juwita/venv/bin/activate && python scripts/cleanup_orphaned_files.py

Cron example (run daily at 3am):
    0 3 * * * cd /home/juwita/juwita && /home/juwita/venv/bin/python scripts/cleanup_orphaned_files.py >> /var/log/juwita_cleanup.log 2>&1
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juwita.settings')
django.setup()

from activity.models import MeetingPhoto
from django.conf import settings
from pathlib import Path
from datetime import datetime


def cleanup_orphaned_files(dry_run=False):
    """Remove orphaned photo files from the media directory."""
    media_root = Path(settings.MEDIA_ROOT)
    photos_dir = media_root / 'meeting_photos'

    if not photos_dir.exists():
        print(f"Photos directory does not exist: {photos_dir}")
        return

    # Get all file paths referenced in database
    db_files = set()
    for photo in MeetingPhoto.objects.all():
        if photo.image:
            db_files.add(Path(photo.image.path).name)

    # Find files on disk
    disk_files = set()
    for f in photos_dir.iterdir():
        if f.is_file():
            disk_files.add(f.name)

    # Find orphaned files (on disk but not in DB)
    orphaned = disk_files - db_files

    print(f"[{datetime.now().isoformat()}] Cleanup Report")
    print(f"  Files in database: {len(db_files)}")
    print(f"  Files on disk: {len(disk_files)}")
    print(f"  Orphaned files: {len(orphaned)}")

    if not orphaned:
        print("  No orphaned files to remove.")
        return

    total_size = 0
    for filename in orphaned:
        file_path = photos_dir / filename
        file_size = file_path.stat().st_size
        total_size += file_size

        if dry_run:
            print(f"  [DRY RUN] Would delete: {filename} ({file_size / 1024:.1f} KB)")
        else:
            file_path.unlink()
            print(f"  Deleted: {filename} ({file_size / 1024:.1f} KB)")

    print(f"  Total space {'would be ' if dry_run else ''}freed: {total_size / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Cleanup orphaned meeting photos')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    args = parser.parse_args()

    cleanup_orphaned_files(dry_run=args.dry_run)
