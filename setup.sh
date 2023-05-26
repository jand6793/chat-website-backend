#!/bin/bash

echo "host    chat_data      backend      127.0.0.1/32            md5" >> /etc/postgresql/13/main/pg_hba.conf

# start postgresql
service postgresql start 

# wait for postgresql to start
until sudo -u postgres psql -c '\l'; do
  sleep 0.1 
done

# run the setup commands
sudo -u postgres psql -c "ALTER USER postgres PASSWORD '${POSTGRES_PASSWORD}';"
sudo -u postgres psql -c "CREATE USER backend WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT NOREPLICATION CONNECTION LIMIT 100 PASSWORD '${BACKEND_PASSWORD}';"
sudo -u postgres psql -c "CREATE DATABASE chat_data WITH OWNER = backend ENCODING = 'UTF8' CONNECTION LIMIT = 100;"

PGPASSWORD=${BACKEND_PASSWORD} psql -U backend -h localhost -d chat_data -c "CREATE SCHEMA chat;"
PGPASSWORD=${BACKEND_PASSWORD} psql -U backend -h localhost -d chat_data -c "CREATE TABLE chat.users ( id bigint NOT NULL GENERATED ALWAYS AS IDENTITY, created timestamp with time zone DEFAULT current_timestamp, last_modified timestamp with time zone DEFAULT current_timestamp, deleted boolean NOT NULL DEFAULT FALSE, PRIMARY KEY (id), full_name text NOT NULL, username text UNIQUE NOT NULL, description text, hashed_password text NOT NULL );"
PGPASSWORD=${BACKEND_PASSWORD} psql -U backend -h localhost -d chat_data -c "CREATE TABLE chat.messages ( id bigint NOT NULL GENERATED ALWAYS AS IDENTITY, created timestamp with time zone DEFAULT current_timestamp, last_modified timestamp with time zone DEFAULT current_timestamp, deleted boolean NOT NULL DEFAULT FALSE, PRIMARY KEY (id), source_user_id bigint NOT NULL, target_user_id bigint NOT NULL, content text NOT NULL );"
