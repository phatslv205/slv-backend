#!/bin/bash

cd "$(dirname "$0")"

# Chạy Flask bằng Gunicorn với 4 worker + gevent
gunicorn -w 4 -k gevent -b 127.0.0.1:8000 app:app
