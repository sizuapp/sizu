#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
gunicorn sizu_project.wsgi