#!/bin/bash
# LMSP Database Backup Script
# Backs up lmsp.db with rotation and compression

set -e

DB_PATH="/root/learn-me-some-py/data/lmsp.db"
BACKUP_DIR="/root/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lmsp_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Only backup if database exists
if [ -f "$DB_PATH" ]; then
    # Use sqlite3 .backup for safe online backup
    sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"
    echo "Backup created: $BACKUP_FILE"
else
    echo "Database not found at $DB_PATH, skipping backup"
    exit 0
fi
