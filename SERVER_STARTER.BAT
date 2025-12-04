start cmd /k ".venv\Scripts\celery.exe -A messenger_project worker -l info"
start cmd /k ".venv\Scripts\celery.exe -A messenger_project beat -l info"
start cmd /k ".venv\Scripts\python.exe manage.py runserver"