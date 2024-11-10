#!/bin/sh

cd /opt/app-root/src
python /tmp/debugpy --listen 0.0.0.0:5678 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 1 --reload