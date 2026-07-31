#!/bin/bash
BACKUP_DIR="/opt/backup"
BUCKET="monitoring-backup-$(hostname)-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
tar -czf /tmp/backup.tar.gz $BACKUP_DIR
aws s3 cp /tmp/backup.tar.gz s3://$BUCKET/ --endpoint-url=https://storage.yandexcloud.net
rm -f /tmp/backup.tar.gz
