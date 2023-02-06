#!/bin/sh

gunicorn core.wsgi -b 0.0.0.0:5000 -w 5 --max-requests 100