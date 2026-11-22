#!/usr/bin/env bash
set -euo pipefail

test_db="${POSTGRES_TEST_DB:-${POSTGRES_DB}_test}"

psql \
  --username "$POSTGRES_USER" \
  --dbname postgres \
  --set test_db="$test_db" \
  --set owner="$POSTGRES_USER" \
  --set ON_ERROR_STOP=1 <<'SQL'
SELECT format('CREATE DATABASE %I OWNER %I', :'test_db', :'owner')
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_database
    WHERE datname = :'test_db'
)
\gexec
SQL
