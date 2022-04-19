#!/bin/bash

set -euo pipefail

./manage.py collectstatic --no-input
exec "$@"
