#!/bin/sh

cd /code
python /tmp/debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload