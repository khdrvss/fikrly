# Fikrly VPS Migration Runbook

This guide shows how to copy the project to your VPS folder and migrate the PostgreSQL database safely.

Target VPS:
- Host: `38.242.242.133`
- User: `maymun`
- Project folder: `/home/maymun/fikrly`

---

## 1) Prerequisites

Run on **local machine**:

```bash
cd /home/ubuntu/projects/fikrly
git status
git push origin main
```

Run on **VPS**:

```bash
ssh maymun@38.242.242.133
docker --version
docker compose version
```

If Docker commands fail with permission denied, use `sudo` before docker commands.

---

## 2) Copy/Update Project in VPS Folder

If folder does not exist:

```bash
ssh maymun@38.242.242.133
git clone https://github.com/khdrvss/fikrly.git /home/maymun/fikrly
cd /home/maymun/fikrly
```

If folder already exists:

```bash
ssh maymun@38.242.242.133
cd /home/maymun/fikrly
git fetch origin
git checkout main
git pull --rebase origin main
```

---

## 3) Prepare Environment on VPS

```bash
cd /home/maymun/fikrly
cp -n .env.production .env || true
# Edit .env and verify DB/Redis/secret values
nano .env
```

Bring stack up:

```bash
cd /home/maymun/fikrly
sudo docker compose up -d --build
sudo docker compose ps
```

---

## 4) Create Local PostgreSQL Dump

Run on local machine:

```bash
cd /home/ubuntu/projects/fikrly
TS=$(date +%Y%m%d_%H%M%S)
DUMP_FILE="/tmp/fikrly_prod_${TS}.dump"
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$DUMP_FILE"
ls -lh "$DUMP_FILE"
echo "$DUMP_FILE"
```

---

## 5) Transfer Dump to VPS

Run on local machine (replace dump filename if needed):

```bash
scp /tmp/fikrly_prod_YYYYMMDD_HHMMSS.dump maymun@38.242.242.133:/tmp/
```

---

## 6) Safety Backup of Current VPS DB (Important)

Run on VPS:

```bash
cd /home/maymun/fikrly
TS=$(date +%Y%m%d_%H%M%S)
VPS_BACKUP="/tmp/vps_pre_restore_${TS}.dump"
sudo docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$VPS_BACKUP"
ls -lh "$VPS_BACKUP"
```

---

## 7) Restore Dump into VPS PostgreSQL

Run on VPS (replace filename):

```bash
cd /home/maymun/fikrly
sudo docker cp /tmp/fikrly_prod_YYYYMMDD_HHMMSS.dump fikrly_db:/tmp/fikrly_prod.dump
sudo docker compose exec -T db sh -lc 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges /tmp/fikrly_prod.dump'
```

---

## 8) Migrate + Validate App

Run on VPS:

```bash
cd /home/maymun/fikrly
sudo docker compose exec -T web python manage.py migrate --noinput
sudo docker compose exec -T web python manage.py check
curl -s -o /tmp/health.out -w 'HTTP=%{http_code}\n' http://localhost/health/
cat /tmp/health.out
```

Expected:
- Migrations: `No migrations to apply` (or applies cleanly)
- Django check: `System check identified no issues`
- Health endpoint: `HTTP=200` and healthy JSON payload

---

## 9) Sync Uploaded Media (if needed)

If uploads are not already present on VPS:

Run on local machine:

```bash
rsync -avz /home/ubuntu/projects/fikrly/media/ maymun@38.242.242.133:/home/maymun/fikrly/media/
```

Then on VPS:

```bash
cd /home/maymun/fikrly
sudo docker compose restart web nginx
```

---

## 10) Rollback (if needed)

Use the VPS backup created in step 6:

```bash
cd /home/maymun/fikrly
sudo docker cp /tmp/vps_pre_restore_YYYYMMDD_HHMMSS.dump fikrly_db:/tmp/vps_pre_restore.dump
sudo docker compose exec -T db sh -lc 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges /tmp/vps_pre_restore.dump'
sudo docker compose exec -T web python manage.py migrate --noinput
```

---

## 11) Cleanup Temp Dump Files

On VPS:

```bash
rm -f /tmp/fikrly_prod_*.dump
sudo docker exec fikrly_db rm -f /tmp/fikrly_prod.dump /tmp/vps_pre_restore.dump || true
```

On local machine:

```bash
rm -f /tmp/fikrly_prod_*.dump
```

---

## Quick One-Line Verification

```bash
ssh maymun@38.242.242.133 'cd /home/maymun/fikrly && sudo docker compose ps && curl -s http://localhost/health/'
```
