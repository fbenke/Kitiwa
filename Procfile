web: python manage.py collectstatic --noinput; python manage.py migrate; newrelic-admin run-program python manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 3
worker: celery -A kitiwa worker -l info
