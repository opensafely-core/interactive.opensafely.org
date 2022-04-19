#!/bin/bash

set -euo pipefail

./manage.py migrate

exec gunicorn interactive.wsgi --config=deploy/gunicorn.conf.py
