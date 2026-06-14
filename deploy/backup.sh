#!/usr/bin/env bash
# Daily backup of Paideia SQLite DB. Hot snapshot using sqlite3 .backup
# (safer than copying mid-write). Keeps last 14 days, gzipped.
set -euo pipefail

APP_DIR="/opt/paideia/app"
DB="$APP_DIR/db/paideia.db"
BACKUP_DIR="/srv/paideia/backup"
STAMP=$(date -u +%Y-%m-%d_%H%M)
KEEP_DAYS=14

mkdir -p "$BACKUP_DIR"

if [[ ! -f "$DB" ]]; then
    echo "ERR: DB not found at $DB"; exit 1
fi

OUT="$BACKUP_DIR/paideia-$STAMP.db"

# Use sqlite3 .backup for hot snapshot (handles WAL correctly)
if command -v sqlite3 >/dev/null; then
    sqlite3 "$DB" ".backup '$OUT'"
else
    # fallback: file copy (safe with WAL mode where db is mostly read-only)
    cp "$DB" "$OUT"
fi

gzip -9 "$OUT"
echo "OK $OUT.gz $(du -h $OUT.gz | cut -f1)"

# Prune old
find "$BACKUP_DIR" -name 'paideia-*.db.gz' -mtime +$KEEP_DAYS -delete

# Also dump content/ markdown since it's source of truth
CONTENT_TGZ="$BACKUP_DIR/content-$STAMP.tar.gz"
tar -czf "$CONTENT_TGZ" -C "$APP_DIR" content/
echo "OK $CONTENT_TGZ $(du -h $CONTENT_TGZ | cut -f1)"
find "$BACKUP_DIR" -name 'content-*.tar.gz' -mtime +$KEEP_DAYS -delete
