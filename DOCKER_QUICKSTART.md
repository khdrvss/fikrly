# 🐳 Docker Quick Start Guide

## Launch Entire Project (One Command!)

```bash
# Copy environment file
cp .env.docker .env

# Start everything!
make up

# OR using docker-compose directly
docker-compose up -d
```

That's it! 🎉

## Access Your Application

- **Website:** https://fikrly.uz
- **Admin:** https://fikrly.uz/admin/
- **Health Check:** https://fikrly.uz/health/
- **Local Dev:** http://localhost:8000 (development mode)

## First Time Setup

### 1. Create Admin User
```bash
make superuser
# OR
docker-compose exec web python manage.py createsuperuser
```

### 2. Check Everything is Running
```bash
make ps
# You should see 4 containers running:
# - fikrly_db (PostgreSQL)
# - fikrly_redis (Redis)
# - fikrly_web (Django)
# - fikrly_nginx (Nginx)
```

## Common Commands

```bash
# View logs
make logs

# Stop everything
make down

# Restart
make restart

# Run Django commands
make shell          # Django shell
make migrate        # Run migrations
make test           # Run tests

# Backup database
make backup

# Clean everything (WARNING: Deletes data!)
make clean
```

## Development Mode

For development with hot-reload:

```bash
make up-dev
# Access at: http://localhost:8000 (not fikrly.uz in dev mode)
```

## Need Help?

See full documentation: `docker/README.md`

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8080:80"  # Change 80 to 8080
```

### Container Won't Start
```bash
# Check logs
make logs

# Rebuild
make rebuild
```

### Reset Everything
```bash
# Clean and restart
make clean
make up
make superuser
```

## Production Deployment

See `docker/README.md` for complete production deployment guide including:
- SSL/HTTPS setup
- Environment variables
- Security hardening
- Backup automation
- Monitoring
