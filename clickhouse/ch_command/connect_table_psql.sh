#!/bin/bash
set -e

clickhouse-client -q "CREATE TABLE ${CLICKHOUSE_DB}.events_from_postgres (
    event_id UInt32,
    user_id Int32,
    movie_id Int32,
    event_type String,
    event_time DateTime
)
ENGINE = PostgreSQL('server_subscription:5432', 'postgres_subscriber', 'events', 'postgres', '$POSTGRES_SUBSCRIPTION_PASSWORD', 'raw');"

