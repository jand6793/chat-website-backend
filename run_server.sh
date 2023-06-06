#!/bin/bash

# service postgresql start

# # wait for postgresql to start
# until sudo -u postgres psql -c '\l'; do
#   sleep 0.1 
# done

uvicorn src.app.api.server:app --host 20.106.172.11 --port 80