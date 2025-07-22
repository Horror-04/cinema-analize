#!/bin/bash

psql -d postgres_subscriber -c "CREATE SCHEMA raw;"

psql -d postgres_subscriber -c 'CREATE TABLE raw.events (
    event_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    movie_id INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    event_time TIMESTAMP WITHOUT TIME ZONE NOT NULL
);'

psql -d postgres_subscriber -c "
	CREATE SUBSCRIPTION db_test_sub
    CONNECTION 'host=server_publicist
                port=5432
                user=$POSTGRES_USER
				password=$POSTGRES_PASSWORD
				dbname=postgres_publicist'
	PUBLICATION db_pub
	with (
		create_slot = false,
		enabled = false,
		slot_name = my_pub_slot
		);"

psql -d postgres_subscriber -c "ALTER SUBSCRIPTION db_test_sub ENABLE;"


