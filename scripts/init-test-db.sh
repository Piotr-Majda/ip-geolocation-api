#!/bin/bash
set -e

echo "Initializing additional databases..."

# The script runs as the postgres user, or the user specified by POSTGRES_USER.
# It will connect to the default 'postgres' database (or the one specified by POSTGRES_DB if psql defaults to it)
# to execute these database creation commands.
# Using --dbname "postgres" is explicit and safe for creating other databases.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
    -- Create the test database (if not already created by another mechanism or previous run)
    CREATE DATABASE "geolocation-test";
    GRANT ALL PRIVILEGES ON DATABASE "geolocation-test" TO "$POSTGRES_USER";

    -- Add more CREATE DATABASE and GRANT statements here as needed

EOSQL

echo "Additional database creation process completed."