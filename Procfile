web: sh -c 'flask --app app init-db && flask --app app seed && gunicorn app:app --bind 0.0.0.0:${PORT:-8080}'
