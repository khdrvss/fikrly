# Folder-by-folder guide

Top-level
- `myproject/` — Django project (ASGI/WSGI, global settings, root URLs)
- `frontend/` — Main Django app (models, views, templates, admin, forms)
- `public/` — Public static assets served as-is (favicon, manifest)
- `media/` — Uploaded files (avatars, company_library, attachments)
- `frontend/static/` — Tailwind source and built CSS
- `templates/` — (If present) shared templates — primary templates live in `frontend/templates`
- `scripts/` — helper scripts for development
- `requirements.txt` — Python dependencies
- `package.json` — Frontend dependencies and scripts
- `manage.py` — Django management entrypoint

Inside `frontend/`
- `models.py` — Data models: Company, Review, ReviewReport, UserProfile, ActivityLog, PhoneOTP, CompanyClaim
- `views.py` — Page and action views: company detail, review submission, report, manager flows, claim/verify
- `forms.py` — Django forms for profile, company manager edit, report, owner response, claim
- `admin.py` — Django admin registrations and inlines (ActivityLog, CompanyClaim)
- `urls.py` — App URL patterns (mounted in project urls)
- `signals.py` — Post-save hooks (telegrams, logs)
- `middleware.py` — NoCache & PostLoginRedirect middlewares
- `templates/` — UI templates under `pages/` and `account/`
- `static/` — Built CSS (main.css) and JS (if any)
- `management/commands/` — Custom manage.py commands (smtp check, test sms, etc.)
- `migrations/` — Schema migrations

Config
- `myproject/settings.py` — env loader, installed apps, email/SMS config
- `.env` — local environment variables (not committed)
- `myproject/urls.py` — sitewide URL includes

Data & media
- `frontend/data/` — category labels and other data
- `media/` — uploaded avatars, library images
- `public/` — static assets served directly (favicon, manifest, js)

Ops & scripts
- `scripts/` — Windows/PowerShell helpers for local dev
- `tasks` — VS Code tasks.json configured for Django (makemigrations, migrate, check)

Where to start
- Read `myproject/settings.py` for config
- Browse `frontend/views.py` and `frontend/templates/pages/` for UI flow
- See `frontend/models.py` and `frontend/admin.py` for data and admin UI
