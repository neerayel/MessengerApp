Basic django web-chat app with friendlist and message encryption

How to launch:
1) Start Postgres and Redis
  - Start cmd in project directory
  - run docker-compose up -d
  - wait for docker to stop assembling a container

2) Create virtual environment:
  - python -m venv .venv
  - .venv\Scripts\Activate.bat (or use ENV_CONSOLE.BAT if on windows)

3) Make migrations
  - python manage.py makemigrations
  - python manage.py migrate

4) Create super user
  - python manage.py createsuperuser
  - Do what it ask to do

5) Launch:
  - Ensure docker container is running
  - Autostart (for windows):
    + SERVER_STARTER.BAT
  - Manual:
    + open 3 console windows and activate virtual environment ( .venv\Scripts\Activate.bat (or use ENV_CONSOLE.BAT if on windows) )
    + (first window) celery -A messenger_project worker -l info
    + (second window) celery -A messenger_project beat -l info
    + (third window) python manage.py runserver
