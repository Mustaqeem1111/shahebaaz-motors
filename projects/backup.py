"""
Shahebaz Motors - Automatic Database Backup System
==================================================
Creates daily backups of database and uploads.

Run manually:
    python backup.py

Schedule with Windows Task Scheduler:
    - Daily at 3:00 AM
    - Program: python
    - Arguments: backup.py
    - Start in: D:\MYJAVA\FRONTEND\projects
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta

from config import DATABASE_PATH, UPLOAD_FOLDER


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKUP_FOLDER = os.path.join(BASE_DIR, "backups")

# Keep backups for this many days
BACKUP_RETENTION_DAYS = 7

# Max backups to keep
MAX_BACKUPS = 30


# =========================================================
# CREATE BACKUP
# =========================================================

def create_backup():
    """
    Create a full backup of database and uploads folder.
    Returns the backup path.
    """

    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_name = f"shahebaz_backup_{timestamp}"
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)

    os.makedirs(backup_path, exist_ok=True)

    # ---------- BACKUP DATABASE ----------
    if os.path.isfile(DATABASE_PATH):
        try:
            # Use SQLite backup API (safe even if DB is being written)
            source = sqlite3.connect(DATABASE_PATH)
            dest = sqlite3.connect(
                os.path.join(backup_path, "shahebaz_motors.db")
            )

            with dest:
                source.backup(dest)

            source.close()
            dest.close()

            print(f"[OK] Database backed up")
        except Exception as e:
            print(f"[FAIL] Database backup failed: {e}")
    else:
        print(f"[WARN] Database not found: {DATABASE_PATH}")

    # ---------- BACKUP UPLOADS ----------
    if os.path.isdir(UPLOAD_FOLDER):
        try:
            uploads_backup = os.path.join(backup_path, "uploads")
            shutil.copytree(UPLOAD_FOLDER, uploads_backup)

            file_count = len(os.listdir(UPLOAD_FOLDER))
            print(f"[OK] Uploads backed up ({file_count} files)")
        except Exception as e:
            print(f"[FAIL] Uploads backup failed: {e}")
    else:
        print(f"[WARN] Uploads folder not found")

    print(f"[INFO] Backup created: {backup_path}")

    return backup_path


# =========================================================
# CLEANUP OLD BACKUPS
# =========================================================

def cleanup_old_backups():
    """Delete backups older than retention period."""

    if not os.path.isdir(BACKUP_FOLDER):
        return

    cutoff = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)

    deleted_count = 0

    backups = []

    for item in os.listdir(BACKUP_FOLDER):
        item_path = os.path.join(BACKUP_FOLDER, item)

        if not os.path.isdir(item_path):
            continue

        if not item.startswith("shahebaz_backup_"):
            continue

        mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
        backups.append((item_path, mod_time))

    # Sort by time (oldest first)
    backups.sort(key=lambda x: x[1])

    # Delete old ones
    for backup_path, mod_time in backups:
        if mod_time < cutoff:
            try:
                shutil.rmtree(backup_path)
                deleted_count += 1
                print(f"[DEL] Old backup removed: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"[FAIL] Could not delete {backup_path}: {e}")

    # Enforce max backups
    remaining = [(p, t) for p, t in backups if os.path.isdir(p)]

    if len(remaining) > MAX_BACKUPS:
        excess = len(remaining) - MAX_BACKUPS

        for i in range(excess):
            backup_path, _ = remaining[i]

            try:
                shutil.rmtree(backup_path)
                deleted_count += 1
                print(f"[DEL] Excess backup removed: {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"[FAIL] Could not delete {backup_path}: {e}")

    if deleted_count == 0:
        print("[INFO] No old backups to delete")
    else:
        print(f"[INFO] Total deleted: {deleted_count}")


# =========================================================
# LIST BACKUPS
# =========================================================

def list_backups():
    """Print all available backups."""

    if not os.path.isdir(BACKUP_FOLDER):
        print("No backups folder found.")
        return

    backups = sorted(os.listdir(BACKUP_FOLDER), reverse=True)

    if not backups:
        print("No backups available.")
        return

    print()
    print("=" * 60)
    print(f"AVAILABLE BACKUPS ({len(backups)})")
    print("=" * 60)

    for backup in backups:
        backup_path = os.path.join(BACKUP_FOLDER, backup)

        if not os.path.isdir(backup_path):
            continue

        total_size = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        size_mb = total_size / (1024 * 1024)

        mod_time = datetime.fromtimestamp(os.path.getmtime(backup_path))

        print(f"  {backup}")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Date: {mod_time.strftime('%d %b %Y, %I:%M %p')}")
        print()

    print("=" * 60)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SHAHEBAZ MOTORS - BACKUP SYSTEM")
    print("=" * 60)
    print()

    backup_path = create_backup()

    print()

    cleanup_old_backups()

    print()

    list_backups()

    print()
    print("=" * 60)
    print("[DONE] BACKUP COMPLETED")
    print("=" * 60)
    print()