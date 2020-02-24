web: gunicorn mysite.wsgi
release: python manage.py migrate
heroku config:set DISABLE_COLLECTSTATIC=1