#!/bin/sh

exec uvicorn --app-dir=./pysrc --factory pycro_scrape:create_app --host=0.0.0.0 --port=$PORT
