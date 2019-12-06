#!/usr/bin/env bash

echo "UPGRADING DATABASE SCHEMA YO"
#flask db init
#flask db migrate
#flask db upgrade
echo "finish upgrading 2"

#python3 ./mysql-seed/seed_data.py

flask run --host=0.0.0.0