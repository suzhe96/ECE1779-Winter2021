gunicorn --bind 0.0.0.0:5000 --workers=1 --threads=2 --access-logfile access.log --error-logfile error.log --chdir /home/ubuntu/Desktop/ECE1779-Winter2021/A1 app:app
