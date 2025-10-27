#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASS" --silent; do
    sleep 1
done

echo "Database is ready. Initializing flag..."
php /var/www/html/init_flag.php

echo "Starting Apache..."
exec apache2-foreground