gunicorn --bind 0.0.0.0:5000 --workers=20 --threads=2 --access-logfile access.log --error-logfile error.log app:a1_webapp
