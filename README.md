# INTERNOVA Django REST API for Intern Management

Internal-use backend for the INTERNOVA platform. This repository provides the Django REST Framework API used to manage intern onboarding, assessments, attendance, DAR submissions, projects, assets, leave requests, calendar data, notifications, and feature access controls.

This README is intended for all project stakeholders:
- backend developers
- frontend developers
- deployment and infrastructure teammates
- reviewers and maintainers

## Internal Use

This repository is for internal team use only. Do not commit real secrets, production credentials, or private environment files such as `.env`.

## What This Project Includes

- Django 6.x backend with Django REST Framework
- JWT authentication with role-based access
- Custom `User` model for `superadmin`, `staffadmin`, and `intern`
- App-based architecture with business logic centralized in `services.py`
- PostgreSQL-ready configuration for local or hosted databases
- Supabase-compatible pooled Postgres support
- S3-compatible media storage support via `django-storages`

## Core Features

- Account management and JWT auth
- Batch management
- Intern profiles and registration approval flow
- Assessments, pages, questions, attempts, and server-side scoring
- Attendance clock-in and clock-out with computed hours and status
- Daily Activity Report uploads
- Calendar settings, holidays, and events
- Leave requests with business-day computation
- Project assignment
- Laptop inventory and issue reporting
- Notifications with per-user read state
- Feature access configuration

## Tech Stack

- Python 3.12+
- Django 6.x
- Django REST Framework
- PostgreSQL
- SimpleJWT
- django-filter
- django-cors-headers
- django-storages
- boto3
- python-decouple

## Project Structure

```text
internova-backend-api/
├── apps/
├── common/
├── config/
├── AGENTS.md
├── CONTEXT.md
├── MEMORY.md
├── PLAN.md
├── README.md
├── SCHEMA.md
├── SKILLS.md
├── STANDARDS.md
├── manage.py
└── requirements.txt
```

## Local Development Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your local environment file

Create `.env` from `.env.example`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Then edit `.env` with your real local values.

### 4. Choose a database

This project supports either of these for local development:

- local PostgreSQL
- hosted PostgreSQL such as Supabase

Example local PostgreSQL `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/internova
```

Example Supabase pooled `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres.username:password@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed development data

```bash
python manage.py seed_dev
```

The seed command is intended for development only and is designed to be idempotent.

### 7. Start the development server

```bash
python manage.py runserver
```

## Recommended Local `.env` Values

For local development, a common starting point is:

```env
SECRET_KEY=replace-with-a-long-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://postgres:password@localhost:5432/internova
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

If you are not using S3-compatible media storage locally, you can keep the production-only `AWS_*` values unset in local development as long as you are not loading the production settings module.

## Environment Variables

The tracked template lives in `.env.example`.

Important variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: `True` for local development, `False` for production
- `ALLOWED_HOSTS`: comma-separated backend hostnames
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins
- `CSRF_TRUSTED_ORIGINS`: comma-separated trusted origins for CSRF-protected requests
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`: access token lifetime
- `JWT_REFRESH_TOKEN_LIFETIME_DAYS`: refresh token lifetime

Production storage variables:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_CUSTOM_DOMAIN`

Production security variables:

- `SECURE_SSL_REDIRECT`
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`

## Common Development Commands

Run the server:

```bash
python manage.py runserver
```

Create migrations:

```bash
python manage.py makemigrations <app>
```

Apply migrations:

```bash
python manage.py migrate
```

Run all app tests:

```bash
python manage.py test apps --verbosity=2
```

Run one app's tests:

```bash
python manage.py test apps.<app> --verbosity=2
```

Run deploy checks:

```bash
python manage.py check --deploy --settings=config.settings.prod
```

Seed development data:

```bash
python manage.py seed_dev
```

## Architecture Notes

- All business logic belongs in `services.py`
- Views should stay thin and HTTP-focused
- Serializers should validate shape and field-level rules
- Cross-app service imports should be function-level to avoid circular imports
- Sensitive fields such as passwords and assessment answer keys must never be exposed improperly

For implementation rules and deeper architecture guidance, use the internal docs listed below.

## Production Deployment Notes

Production settings live in `config/settings/prod.py`.

Before deploying:

1. Set `DEBUG=False`
2. Use a strong production `SECRET_KEY`
3. Set a valid production `DATABASE_URL`
4. Set non-empty `ALLOWED_HOSTS`
5. Set non-empty `CORS_ALLOWED_ORIGINS`
6. Set non-empty `CSRF_TRUSTED_ORIGINS`
7. Configure S3-compatible media storage for DAR uploads and avatars
8. Run migrations
9. Run tests
10. Run deploy checks

Recommended production verification:

```bash
python manage.py test apps --verbosity=2
python manage.py check --deploy --settings=config.settings.prod
```

### Production Storage

This project supports S3-compatible object storage. For Supabase Storage S3 compatibility, typical production values look like:

```env
AWS_STORAGE_BUCKET_NAME=internova-media
AWS_S3_ENDPOINT_URL=https://<project-ref>.supabase.co/storage/v1/s3
AWS_S3_CUSTOM_DOMAIN=
```

Use a private bucket by default unless you have a deliberate public/CDN setup.

### Production Security

Typical production values:

```env
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=False
```

Set `SECURE_HSTS_PRELOAD=True` only if your domain setup is intentionally ready for HSTS preload behavior.

## Render Deployment

This repository now includes:

- `render.yaml` for Render service configuration
- `build.sh` for dependency install and static collection
- `gunicorn` as the production web server
- `whitenoise` for serving collected static files

### Recommended Render Service Type

Use a Render Web Service with:

- runtime: Python
- settings module: `config.settings.prod`
- start command: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Render Build and Start Flow

The repo is configured for this deployment flow:

1. Install dependencies
2. Collect static files
3. Run migrations
4. Start Gunicorn

`render.yaml` already defines:

- build command
- start command
- required environment variable placeholders

To stay compatible with Render free-plan web services, migrations are run at startup before Gunicorn begins serving requests.

### Render Environment Variables

Set these in Render:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
DEBUG=False
ALLOWED_HOSTS=<your-render-service>.onrender.com
CORS_ALLOWED_ORIGINS=https://<your-frontend-domain>
CSRF_TRUSTED_ORIGINS=https://<your-frontend-domain>
DATABASE_URL=<your-postgres-connection-string>
SECRET_KEY=<strong-random-secret>
AWS_ACCESS_KEY_ID=<your-s3-access-key>
AWS_SECRET_ACCESS_KEY=<your-s3-secret-key>
AWS_STORAGE_BUCKET_NAME=internova-media
AWS_S3_REGION_NAME=<your-storage-region>
AWS_S3_ENDPOINT_URL=https://<your-project-ref>.supabase.co/storage/v1/s3
AWS_S3_CUSTOM_DOMAIN=
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=False
```

If your frontend has both production and preview origins, add them as comma-separated values for:

- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

### Render Host Example

If Render gives you a service URL like:

```text
https://internova-backend-api.onrender.com
```

then use:

```env
ALLOWED_HOSTS=internova-backend-api.onrender.com
```

### Frontend Origin Example

If your frontend is hosted at:

```text
https://internova.vercel.app
```

then use:

```env
CORS_ALLOWED_ORIGINS=https://internova.vercel.app
CSRF_TRUSTED_ORIGINS=https://internova.vercel.app
```

### After Deploying on Render

After the first successful deploy:

1. Open the Render service URL
2. Test a known API route
3. Confirm media uploads reach the configured bucket
4. Confirm CORS works from the frontend
5. Run a login flow and a representative protected endpoint

## Internal Documentation

For deeper project detail, refer to:

- `AGENTS.md` for agent workflow and hard-stop rules
- `CONTEXT.md` for project overview, endpoint coverage, and business rules
- `SCHEMA.md` for database structure and model expectations
- `STANDARDS.md` for coding conventions and architecture rules
- `PLAN.md` for build progress and task tracking
- `MEMORY.md` for known bugs, quirks, and past fixes
- `SKILLS.md` for slash-command workflow definitions

## Notes for Contributors

- Keep changes scoped and app-focused
- Do not manually edit migration files
- Do not place business logic in views or serializers
- Run relevant tests before considering a task complete
- Prefer updating the existing internal docs over creating new ad hoc documentation files
