Basic django web-chat app with friendlist and message encryption

How to launch:
- Start cmd in project directory
- docker-compose up -d
- wait for docker to stop assembling a container

- python -m venv .venv
- .venv\Scripts\Activate.bat (or use ENV_CONSOLE.BAT if on windows)
- python manage.py makemigrations
- python manage.py migrate
  
- python manage.py createsuperuser
- Do what it ask to do

Finally you need 3 console windows with active venv ( .venv\Scripts\Activate.bat (or use ENV_CONSOLE.BAT if on windows) ):
- celery -A messenger worker -l info
- celery -A messenger beat -l info
- python manage.py runserver
