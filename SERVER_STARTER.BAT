start cmd /k ".venv\Scripts\celery.exe -A messenger_project.messenger_project worker -l info"
start cmd /k ".venv\Scripts\celery.exe -A messenger_project.messenger_project beat -l info"
start cmd /k ".venv\Scripts\daphne.exe -b 0.0.0.0 -p 8000 messenger_project.messenger_project.asgi:application"