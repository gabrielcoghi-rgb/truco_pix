# PIXUP Django Project

This project implements user registration/login with JWT, a wallet system, transaction history, and integration with PIXUP for PIX payments.

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in values (SECRET_KEY, DB_*, PIXUP_API_KEY).

3. Run migrations and create a superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Run the development server:

```bash
python manage.py runserver
```

Notes
- PIXUP integration requires a valid `PIXUP_API_KEY` in `.env`.
- For production, configure HTTPS (e.g., via reverse proxy) and set DEBUG=False.
