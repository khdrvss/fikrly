# Fikrly Reviews Platform

A Django-based reviews platform with Tailwind CSS frontend and Telegram notifications.

## Project structure

- Frontend — UI templates, Tailwind CSS, assets (see `frontend/` and docs/folders.md)
- Backend — Django app logic (models, views, forms, admin, signals)
- Config — Project settings, URLs, and environment (`myproject/`, `.env`)
- Data & Media — Data files, uploads, and static/public assets
- Ops & Scripts — Tasks and helper scripts

More details in docs:
- docs/README.md — project map
- docs/folders.md — folder-by-folder guide
- docs/routes.md — URL routes
- docs/models.md — core models

## Getting started

1. Install Python deps: `pip install -r requirements.txt`
2. Install frontend deps: `npm install`
3. Configure environment: copy `.env.example` to `.env` and fill values
4. Run migrations: `python manage.py migrate`
5. Start dev server: `python manage.py runserver 0.0.0.0:8000`

## Frontend (Tailwind CSS)

- Dev: `npm run dev` (watches CSS)
- Build: `npm run build:css`

## Notes

- Email backend defaults to console in DEBUG unless SMTP configured
- Optional Telegram/SMS via env vars
- Phone OTP routes exist but are hidden from UI by default

## 🚀 Features

- **HTML5** - Modern HTML structure with best practices
- **Tailwind CSS** - Utility-first CSS framework for rapid UI development
- **Custom Components** - Pre-built component classes for buttons and containers
- **NPM Scripts** - Easy-to-use commands for development and building
- **Responsive Design** - Mobile-first approach for all screen sizes

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- pip

## 🛠️ Installation

1) Backend deps

```bash
pip install -r requirements.txt
```

2) Frontend deps

```bash
npm install
```

3) Environment

Copy `.env.example` to `.env` and fill in values (see below).

4) Run Django dev server

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## ⚙️ Environment (.env)

Variables read from `.env` in project root:

- DEFAULT_FROM_EMAIL=no-reply@fikrly.uz
- EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend  # optional in DEBUG for real tests
- EMAIL_HOST=smtp.sendgrid.net
- EMAIL_PORT=587
- EMAIL_USE_TLS=true
- EMAIL_HOST_USER=apikey
- EMAIL_HOST_PASSWORD=SG.xxxxxx

SMS (Eskiz.uz):

- ESKIZ_BASE=https://notify.eskiz.uz
- ESKIZ_EMAIL=your@login
- ESKIZ_PASSWORD=your-password
- ESKIZ_FROM=4546  # approved sender or short code

Example file: `.env.example`.

## 📁 Project Structure

See the workspace tree in the repository. Key locations:

- `myproject/settings.py` — settings and .env loader
- `frontend/` — Django app (models, views, templates)
- `media/` — uploads
- `public/` — static assets served alongside app

## 🎨 Styling

Tailwind CSS via `tailwind.config.js`. Build/watch with npm scripts.


## 🧩 Customization

Edit `tailwind.config.js` and `static/tailwind.css` as needed.


## 📦 Build for Production

Build CSS:

```bash
npm run build:css
```

## 📱 Responsive Design

The app is built with responsive design using Tailwind CSS breakpoints:

- `sm`: 640px and up
- `md`: 768px and up
- `lg`: 1024px and up
- `xl`: 1280px and up
- `2xl`: 1536px and up

## 🙏 Notes

Set these env vars to enable Telegram:

- TELEGRAM_BOT_TOKEN
- TELEGRAM_ADMIN_CHAT_IDS
- TELEGRAM_REVIEWS_CHAT_IDS

Tokens/IDs should not be committed. Use `.env` locally or real environment vars in production.

Phone-OTP login:

- Go to /accounts/phone to request an OTP.
- Enter the 6-digit code at /accounts/phone/verify.
- Limits: 1 SMS/minute, max 5/hour per phone; codes expire in 5 minutes.

Built with ❤️ on Rocket.new
