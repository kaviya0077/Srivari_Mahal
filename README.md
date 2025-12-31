# Sri Vari Mahal — Full-stack Project Skeleton

This repository contains a ready-to-use project skeleton based on your previous project:
- **Backend:** Django + Django REST Framework + sqlite
- **Frontend:** React

How to run:
1. Backend:
   - python -m venv venv
   - source venv/bin/activate
   - pip install -r backend/requirements.txt
   - python backend/manage.py migrate
   - python backend/manage.py loaddata backend/sample_bookings.json
   - python backend/manage.py runserver

2. Frontend:
   - cd frontend
   - npm install
   - npm start
