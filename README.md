Basic django web-chat app with friendlist and message encryption

<img width="505" height="314" alt="image" src="https://github.com/user-attachments/assets/510629fe-b51f-433c-b05d-154e4e2cdcf2" />

How to launch:
1) Start Postgres and Redis
  - Start cmd in project directory
  - run docker-compose up -d
  - wait for docker to stop assembling a container

2) Create virtual environment and download all packages:
  - python -m venv .venv
  - .venv\Scripts\Activate.bat (or use ENV_CONSOLE.BAT if on windows)
  - pip install -r reqirements.txt

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
    + (third window) daphne -b 0.0.0.0 -p 8000 messenger_project.asgi:application
