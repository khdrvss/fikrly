# Project Health Report — Fikrly Platform

**Generated:** 2026-03-11 (updated)
**Previous report:** 2026-03-11 (initial audit)
**Environment:** Docker (`web`, `nginx`, `db`, `redis`) on VPS (`vmi3013860`)
**Repository:** https://github.com/khdrvss/fikrly
**Live site:** https://fikrly.uz

---

## Executive Summary

**Overall Status:** ✅ **HEALTHY — All systems operational**

Second update on 2026-03-11. Company slug URLs deployed (migration 0051, all 61 companies backfilled). Dead Celery import removed. `/health/` endpoint wired and returning 200. Email subject prefix added. All 4 Docker containers healthy.

### Current Snapshot

| Check | Status | Detail |
|---|---|---|
| Django system check | ✅ PASSED | `0 issues (0 silenced)` |
| DB migrations | ✅ CURRENT | Applied through `frontend.0051` |
| Docker containers | ✅ ALL HEALTHY | All 4 containers up and healthy |
| GTM integration | ✅ LIVE | Container `GTM-WMVCCB9X` rendering on all pages |
| Google Analytics | ✅ LIVE | `GA_MEASUREMENT_ID=G-VF0K77S81T` active |
| VS Code tasks | ✅ FIXED | Repaired broken `.venv` path in `tasks.json` |
| Static assets | ✅ OK | `collectstatic` runs on Docker build |
| i18n | ✅ OK | Uzbek (default) + Russian, path-based prefix `/ru/` |
| Company slug URLs | ✅ LIVE | `/bizneslar/uzum-market/` — all 61 companies backfilled |
| `/health/` endpoint | ✅ LIVE | Returns `{"status":"healthy",...}` — Docker healthcheck passing |
| `email_notifications.py` | ✅ FIXED | Dead `from celery import shared_task` removed |
| Email subject prefix | ✅ SET | `ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Fikrly] "` |

---

## 1) Runtime Health

### Django System Check
```
.venv/bin/python manage.py check
→ System check identified no issues (0 silenced).
```

### Docker Container Status (2026-03-11)
```
fikrly_nginx   Up (healthy)  0.0.0.0:80->80, 0.0.0.0:443->443
fikrly_web     Up (healthy)  8000/tcp   [rebuilt 2026-03-11]
fikrly_db      Up (healthy)  5432/tcp
fikrly_redis   Up (healthy)  6379/tcp
```

### Gunicorn Configuration
- 4 workers × 2 threads, timeout 60 s
- Binds on `0.0.0.0:8000` (internal, proxied by nginx)
- Access + error logs piped to stdout → docker logs

---

## 2) Database & Migration Health

- Backend: **PostgreSQL 15** (`fikrly_db` container)
- ORM: **Django 5.2.4** with psycopg2-binary
- Migration history:

| Range | Count | Status |
|---|---|---|
| `0001` — `0036` | 36 | ✅ Applied |
| `0037` — `0051` | 15 | ✅ Applied |
| **Total** | **51** | ✅ No pending |

- DB connection pooling: `CONN_MAX_AGE=60` + `CONN_HEALTH_CHECKS=True`
- Redis cache: `django-redis` @ `redis://redis:6379/1` with `allkeys-lru`, 256 MB cap

---

## 3) Analytics & Tag Manager

### Changes made in this audit cycle
| What | File | Status |
|---|---|---|
| GTM script (`<head>`) | `frontend/templates/base.html` L9 | ✅ Live |
| GTM noscript (`<body>`) | `frontend/templates/base.html` L173 | ✅ Live |
| `GTM_ID` setting | `myproject/settings.py` | ✅ Default `GTM-WMVCCB9X` |
| `GTM_ID` context var | `core/context_processors.py` | ✅ Injected globally |
| `GTM_ID` env var | `.env` | ✅ `GTM-WMVCCB9X` |
| Docker image rebuilt | `fikrly_web` | ✅ Deployed |

Both GA4 and GTM are conditional: rendered only when the respective env var is set. GTM fires before other `<head>` tags for optimal tag loading priority.

---

## 4) Security Audit

| Item | Status | Detail |
|---|---|---|
| HTTPS / HSTS | ✅ | `SECURE_HSTS_SECONDS=31536000`, preload, subdomains |
| CSRF | ✅ | `CsrfViewMiddleware` active, secure cookie in prod |
| `X-Frame-Options` | ✅ | `DENY` |
| Content-Type nosniff | ✅ | Enabled |
| Secure cookies | ✅ | `SESSION_COOKIE_SECURE=True` in prod |
| Rate limiting | ✅ | `django-ratelimit` on review submit, login, search API |
| SQL injection | ✅ | ORM only, no raw SQL in views |
| File upload validation | ✅ | Receipt max 5 MB checked in `ReviewForm.clean_receipt` |
| Secret key | ✅ | Loaded from env, never hardcoded |
| DEBUG | ✅ | `False` in production (env controlled) |
| Telegram webhook | ✅ | HMAC secret token validation |
| Health endpoint SSL bypass | ✅ | `SECURE_REDIRECT_EXEMPT=[r"^health/$"]` — internal HTTP only |

---

## 5) Code Metrics

| File | Lines |
|---|---|
| `frontend/models.py` | ~920 |
| `frontend/views/company.py` | ~1 270 |
| `frontend/views/review.py` | ~360 |
| `frontend/views/misc.py` | 286 |
| `frontend/views/profile.py` | 94 |
| `frontend/admin.py` | 1 049 |
| `frontend/signals.py` | 419 |
| `frontend/urls.py` | ~225 |
| `myproject/settings.py` | ~605 |
| `frontend/middleware.py` | 188 |
| **Total (key files)** | **~5 500** |

DB models: **17 models**, **51 migrations**
URL routes: **50+ named routes** across `frontend.urls` + `myproject.urls`
Templates: **23 page templates** + `base.html` + error pages
Management commands: **14 custom commands**
i18n locales: **uz** (default), **ru**

---

## 6) Infrastructure Overview

```
Internet → nginx (TLS, port 80/443)
              ↓ proxy_pass
         gunicorn / Django 5.2.4 (port 8000)
              ↓
         PostgreSQL 15   Redis 7 (cache + sessions)

Healthcheck: curl http://localhost:8000/health/  → 200 {"status":"healthy"}
```

- **Static files:** WhiteNoise (`CompressedManifestStaticFilesStorage`)
- **Media files:** Docker volume → nginx `/media/` alias
- **Backups:** `deploy/backup.sh` (nightly cron)
- **SSL:** Let's Encrypt, auto-renewal via `deploy/ssl_renew.sh`
- **Monitoring:** `deploy/monitor.sh`, Telegram error notifications

---

## 7) Dev Tooling Fixed

| Item | Before | After |
|---|---|---|
| VS Code tasks interpreter | `/home/manjaro/Desktop/.../python` (❌ broken) | `${workspaceFolder}/.venv/bin/python` (✅ local) |
| Duplicate tasks | `makemigrations` × 2, `migrate` × 2 | Deduplicated |
| Problem matchers | Wrong (`$tsc`, `$gcc`, `$eslint`) | Cleared to `[]` |

---

## 8) Completed Changes

### 2026-03-11 — Audit cycle 1
- ✅ Google Tag Manager fully integrated (`GTM-WMVCCB9X`) — head script + body noscript
- ✅ GTM/GA IDs moved to Django settings and `.env`
- ✅ Context processor `core.context_processors.google_analytics` updated
- ✅ VS Code `tasks.json` repaired
- ✅ Docker image rebuilt and `fikrly_web` redeployed

### 2026-03-11 — Audit cycle 2
- ✅ **Company slug URLs** — `Company.slug` field added, migration `0051` with data backfill for all 61 companies. URLs: `/bizneslar/<slug>/` canonical, `/bizneslar/<pk>/` 301-redirects
- ✅ **Dead `from celery import shared_task` import removed** from `frontend/email_notifications.py` (Celery is not installed; would have caused `ImportError` at runtime)
- ✅ **`/health/` endpoint wired** in `myproject/urls.py` — returns `{"status":"healthy","checks":{"database":"ok","cache":"ok","disk":"ok"}}` with 200. `SECURE_REDIRECT_EXEMPT` added so Docker's internal HTTP healthcheck hits it directly without 301
- ✅ **`ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Fikrly] "`** added to `settings.py` — allauth emails now clearly identified in users' inboxes
- ✅ `docker-compose.yml` — no `version:` key (already clean)
- ✅ Canonical `<link rel="canonical">` + hreflang alternates — already present in `base.html`

## 9) Open / Recommended Actions

| Priority | Item |
|---|---|
| P2 | **Sentry** error tracking — currently flying blind on production exceptions |
| P2 | **Google Search Console verification** — Bing/Yandex done; Google missing |
| P2 | **Celery + Beat** — async email delivery, scheduled digest/cleanup tasks |
| P3 | Replace hardcoded `GTM-WMVCCB9X` default in `settings.py` with `""` (stricter 12-factor) |
| P3 | Review image upload count cap (prevent storage abuse) |
| P3 | Password strength meter on registration form |

---

## 10) Verification Commands

```bash
# Django check
.venv/bin/python manage.py check

# Run full test suite
.venv/bin/python manage.py test

# Verify /health/ endpoint
sudo docker exec fikrly_web curl -sf http://localhost:8000/health/

# Verify slug URLs in container
sudo docker exec fikrly_web python manage.py shell -c \
  "from frontend.models import Company; c=Company.objects.first(); print(c.get_absolute_url())"

# Verify GTM in live container
sudo docker exec fikrly_web sh -c "grep -n 'GTM' /app/frontend/templates/base.html"

# Check containers
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Tail live logs
sudo docker compose logs -f web
```

**Report End**


## Executive Summary

**Overall Status:** ✅ **HEALTHY — All systems operational**

Full deep-dig audit executed on 2026-03-11. Django system check passes clean, all 50 DB migrations applied, all 4 Docker containers healthy and live. GTM integration deployed and active. VS Code dev tasks repaired. No critical findings.

### Current Snapshot

| Check | Status | Detail |
|---|---|---|
| Django system check | ✅ PASSED | `0 issues (0 silenced)` |
| DB migrations | ✅ CURRENT | Applied through `frontend.0050` |
| Docker containers | ✅ ALL HEALTHY | `web` up 0d, `nginx/db/redis` up 2w |
| GTM integration | ✅ LIVE | Container `GTM-WMVCCB9X` rendering on all pages |
| Google Analytics | ✅ LIVE | `GA_MEASUREMENT_ID=G-VF0K77S81T` active |
| VS Code tasks | ✅ FIXED | Repaired broken `.venv` path in `tasks.json` |
| Static assets | ✅ OK | `collectstatic` runs on Docker build |
| i18n | ✅ OK | Uzbek (default) + Russian, path-based prefix `/ru/` |

---

## 1) Runtime Health

### Django System Check
```
.venv/bin/python manage.py check
→ System check identified no issues (0 silenced).
```

### Docker Container Status (2026-03-11)
```
fikrly_nginx   Up (healthy)  0.0.0.0:80->80, 0.0.0.0:443->443
fikrly_web     Up (healthy)  8000/tcp   [rebuilt 2026-03-11]
fikrly_db      Up (healthy)  5432/tcp
fikrly_redis   Up (healthy)  6379/tcp
```

### Gunicorn Configuration
- 4 workers × 2 threads, timeout 60 s
- Binds on `0.0.0.0:8000` (internal, proxied by nginx)
- Access + error logs piped to stdout → docker logs

---

## 2) Database & Migration Health

- Backend: **PostgreSQL 15** (`fikrly_db` container)
- ORM: **Django 5.2.4** with psycopg2-binary
- Migration history:

| Range | Count | Status |
|---|---|---|
| `0001` — `0036` | 36 | ✅ Applied |
| `0037` — `0050` | 14 | ✅ Applied |
| **Total** | **50** | ✅ No pending |

- DB connection pooling: `CONN_MAX_AGE=60` + `CONN_HEALTH_CHECKS=True`
- Redis cache: `django-redis` @ `redis://redis:6379/1` with `allkeys-lru`, 256 MB cap

---

## 3) Analytics & Tag Manager

### Changes made in this audit cycle
| What | File | Status |
|---|---|---|
| GTM script (`<head>`) | `frontend/templates/base.html` L9 | ✅ Live |
| GTM noscript (`<body>`) | `frontend/templates/base.html` L173 | ✅ Live |
| `GTM_ID` setting | `myproject/settings.py` | ✅ Default `GTM-WMVCCB9X` |
| `GTM_ID` context var | `core/context_processors.py` | ✅ Injected globally |
| `GTM_ID` env var | `.env` L65 | ✅ `GTM-WMVCCB9X` |
| Docker image rebuilt | `fikrly_web` | ✅ Deployed |

Both GA4 and GTM are conditional: rendered only when the respective env var is set. GTM fires before other `<head>` tags for optimal tag loading priority.

---

## 4) Security Audit

| Item | Status | Detail |
|---|---|---|
| HTTPS / HSTS | ✅ | `SECURE_HSTS_SECONDS=31536000`, preload, subdomains |
| CSRF | ✅ | `CsrfViewMiddleware` active, secure cookie in prod |
| `X-Frame-Options` | ✅ | `DENY` |
| Content-Type nosniff | ✅ | Enabled |
| Secure cookies | ✅ | `SESSION_COOKIE_SECURE=True` in prod |
| Rate limiting | ✅ | `django-ratelimit` on review submit, login |
| SQL injection | ✅ | ORM only, no raw SQL in views |
| File upload validation | ✅ | Receipt max 5 MB checked in `ReviewForm.clean_receipt` |
| Secret key | ✅ | Loaded from env, never hardcoded |
| DEBUG | ✅ | `False` in production (env controlled) |
| Telegram webhook | ✅ | HMAC secret token validation |

---

## 5) Code Metrics

| File | Lines |
|---|---|
| `frontend/models.py` | 898 |
| `frontend/views/company.py` | 1 254 |
| `frontend/views/review.py` | 358 |
| `frontend/views/misc.py` | 286 |
| `frontend/views/profile.py` | 94 |
| `frontend/admin.py` | 1 049 |
| `frontend/signals.py` | 419 |
| `frontend/urls.py` | 221 |
| `myproject/settings.py` | 598 |
| `frontend/middleware.py` | 188 |
| **Total (key files)** | **5 472** |

DB models: **17 models**, **50 migrations**  
URL routes: **50+ named routes** across `frontend.urls` + `myproject.urls`  
Templates: **23 page templates** + `base.html` + error pages  
Management commands: **14 custom commands**  
i18n locales: **uz** (default), **ru**

---

## 6) Infrastructure Overview

```
Internet → nginx (TLS, port 80/443)
              ↓ proxy_pass
         gunicorn / Django 5.2.4 (port 8000)
              ↓
         PostgreSQL 15   Redis 7 (cache + sessions)
```

- **Static files:** WhiteNoise (`CompressedManifestStaticFilesStorage`)
- **Media files:** Docker volume → nginx `/media/` alias
- **Backups:** `deploy/backup.sh` (nightly cron)
- **SSL:** Let's Encrypt, auto-renewal via `deploy/ssl_renew.sh`
- **Monitoring:** `deploy/monitor.sh`, Telegram error notifications

---

## 7) Dev Tooling Fixed

| Item | Before | After |
|---|---|---|
| VS Code tasks interpreter | `/home/manjaro/Desktop/fikrly_reviews_platform/.venv/bin/python` (❌ broken) | `${workspaceFolder}/.venv/bin/python` (✅ local) |
| Duplicate tasks | `makemigrations` × 2, `migrate` × 2 | Deduplicated |
| Problem matchers | Wrong (`$tsc`, `$gcc`, `$eslint`) | Cleared to `[]` |

---

## 8) Completed Changes (This Audit)

- ✅ Google Tag Manager fully integrated (`GTM-WMVCCB9X`) — head script + body noscript
- ✅ GTM/GA IDs moved to Django settings (`GTM_ID`, `GA_MEASUREMENT_ID`) and `.env`
- ✅ Context processor `core.context_processors.google_analytics` updated
- ✅ VS Code `tasks.json` repaired — all tasks now use local `.venv`
- ✅ Docker image rebuilt and `fikrly_web` redeployed with all changes

## 9) Open / Recommended Actions

| Priority | Item |
|---|---|
| P2 | Remove obsolete `version` key from `docker-compose.yml` (compose warning) |
| P2 | `email_notifications.py` references `celery.shared_task` but Celery is not in `requirements.txt` — either add Celery or remove the import |
| P3 | `myproject/urls.py` imports `debug_toolbar` unconditionally inside `if settings.DEBUG` — works but will raise `ImportError` if `django-debug-toolbar` is removed from deps |
| P3 | Consider replacing hardcoded `GTM-WMVCCB9X` default in `settings.py` with empty string and rely solely on `.env` for a stricter 12-factor approach |

---

## 10) Verification Commands

```bash
# Django check
.venv/bin/python manage.py check

# Run full test suite
.venv/bin/python manage.py test

# Verify GTM in live container
sudo docker exec fikrly_web sh -c "grep -n 'GTM' /app/frontend/templates/base.html"

# Check containers
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Tail live logs
sudo docker compose logs -f web
```

**Report End**
