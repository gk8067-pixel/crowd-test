cd ~/crowd-test
mkdir -p frontend/app/surveys/create
pbin frontend/app/surveys/create/page.tsx
[ -f api/celery_work.py ] && mv api/celery_work.py api/celery_worker.py
[ -f api/celery_task.py ] && mv api/celery_task.py api/celery_tasks.py
