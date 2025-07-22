#!/bin/bash

psql -d postgres_publicist -c "CREATE SCHEMA raw;"

psql -d postgres_publicist -c 'CREATE TABLE raw.events (
    event_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    event_time TIMESTAMP WITHOUT TIME ZONE NOT NULL
);'

psql -d postgres_publicist -c "CREATE PUBLICATION db_pub FOR ALL TABLES;"

psql -d postgres_publicist -c "SELECT pg_create_logical_replication_slot('my_pub_slot', 'pgoutput');"