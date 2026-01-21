# 🐳 Fikrly Docker Deployment Guide

Complete Docker containerization for the Fikrly platform.

## 📦 What's Included

- **Django Application** (Python 3.12)
- **PostgreSQL 15** (Database)
- **Redis 7** (Cache)
- **Nginx** (Reverse Proxy & Static Files)
- **Automated Backups**
- **Health Checks**
- **Multi-stage Build** (Optimized images)

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### 1. Setup Environment
```bash
# Copy environment file
cp .env.docker .env

# Edit configuration
nano .env
# Set SECRET_KEY, DB_PASSWORD, etc.
```

### 2. Start Everything
```bash
# Production mode
make up

# OR Development mode
make up-dev
```

### 3. Access Application
- **Application:** http://localhost
- **Admin Panel:** http://localhost/admin/
- **Health Check:** http://localhost/health/

### 4. Create Superuser
```bash
make superuser
```

## 🛠️ Available Commands

### Basic Operations
```bash
make build          # Build Docker images
make up             # Start containers (production)
make up-dev         # Start containers (development)
make down           # Stop containers
make restart        # Restart containers
make logs           # View all logs
make ps             # Show running containers
```

### Django Management
```bash
make shell          # Django shell
make bash           # Bash shell in container
make test           # Run tests
make migrate        # Run migrations
make makemigrations # Create migrations
make collectstatic  # Collect static files
make superuser      # Create superuser
```

### Database Operations
```bash
make db-shell       # PostgreSQL shell
make db-reset       # Reset database
make backup         # Backup DB and media
make restore        # Restore from backup
```

### Deployment
```bash
make deploy-prod    # Full production deployment
make health         # Check application health
make clean          # Remove all containers/volumes
make rebuild        # Rebuild from scratch
```

## 📁 Docker Architecture

```
fikrly/
├── docker-compose.yml          # Main orchestration
├── docker-compose.dev.yml      # Development overrides
├── Dockerfile                  # Multi-stage build
├── .dockerignore              # Exclude files
├── .env.docker                # Environment template
├── Makefile                   # Command shortcuts
│
└── docker/
    ├── nginx/
    │   ├── nginx.conf         # Main config
    │   └── conf.d/
    │       └── default.conf   # Site config
    │
    └── scripts/
        ├── entrypoint.sh      # Container init
        ├── backup.sh          # Backup script
        └── restore.sh         # Restore script
```

## 🔧 Configuration

### Environment Variables (.env)

#### Critical Settings
```bash
DEBUG=False
SECRET_KEY=<50+ random characters>
ALLOWED_HOSTS=localhost,yourdomain.com
DB_PASSWORD=<strong-password>
```

#### Database
```bash
DB_NAME=fikrly_db
DB_USER=fikrly_user
DB_PASSWORD=changeme123
DB_HOST=db
DB_PORT=5432
```

#### Cache
```bash
REDIS_URL=redis://redis:6379/1
```

#### Email
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Docker Compose Services

#### 1. Database (PostgreSQL)
- **Image:** postgres:15-alpine
- **Port:** 5432
- **Volume:** postgres_data
- **Health Check:** pg_isready

#### 2. Cache (Redis)
- **Image:** redis:7-alpine
- **Port:** 6379
- **Volume:** redis_data
- **Max Memory:** 256MB
- **Policy:** allkeys-lru

#### 3. Web (Django)
- **Build:** Multi-stage Dockerfile
- **Port:** 8000 (internal)
- **Volumes:** static, media, logs
- **Workers:** 4 Gunicorn workers
- **Threads:** 2 per worker

#### 4. Nginx (Reverse Proxy)
- **Image:** nginx:1.25-alpine
- **Ports:** 80, 443
- **Features:** Rate limiting, caching, compression

## 🔐 Production Deployment

### Step 1: Prepare VPS
```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin
```

### Step 2: Clone & Configure
```bash
git clone YOUR_REPO fikrly
cd fikrly

# Copy and edit environment
cp .env.docker .env
nano .env  # Fill in production values
```

### Step 3: Generate Secrets
```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate strong database password
openssl rand -base64 32
```

### Step 4: Deploy
```bash
# Build and start
make build
make up

# Check status
make ps
make health
```

### Step 5: SSL Certificate (Let's Encrypt)
```bash
# Install certbot in Nginx container
docker-compose exec nginx sh -c "apk add certbot certbot-nginx"

# Get certificate
docker-compose exec nginx certbot --nginx -d yourdomain.com

# Configure auto-renewal (add to crontab)
0 3 * * 1 docker-compose exec nginx certbot renew --quiet
```

## 📊 Monitoring

### View Logs
```bash
# All services
make logs

# Specific service
make logs-web
make logs-nginx
make logs-db
```

### Health Checks
```bash
# Application health
curl http://localhost/health/

# Database connection
docker-compose exec db pg_isready

# Redis connection
docker-compose exec redis redis-cli ping
```

### Resource Usage
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Volume sizes
docker system df -v
```

## 🔄 Backup & Restore

### Automatic Backup
```bash
# Run backup
make backup

# Backups saved to ./backups/
ls -lh backups/
```

### Scheduled Backups (Cron)
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /path/to/fikrly && make backup
```

### Restore from Backup
```bash
# List available backups
make restore

# Restore specific backup
./docker/scripts/restore.sh 20260121_150000
```

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs web

# Check configuration
docker-compose config

# Rebuild
make rebuild
```

### Database connection errors
```bash
# Check database is running
docker-compose ps db

# Check health
docker-compose exec db pg_isready

# Reset database
make db-reset
```

### Static files not loading
```bash
# Collect static files
make collectstatic

# Check Nginx config
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

### Permission errors
```bash
# Fix volume permissions
docker-compose exec web chown -R appuser:appuser /app
```

### Out of disk space
```bash
# Clean unused images
docker system prune -a

# Clean volumes (careful!)
docker volume prune
```

## 🚀 Performance Tuning

### Gunicorn Workers
Edit `docker-compose.yml`:
```yaml
command: gunicorn --workers 8 --threads 4 ...
# Workers = (2 × CPU cores) + 1
# Threads = 2-4 per worker
```

### PostgreSQL Connection Pool
Edit `docker-compose.yml`:
```yaml
environment:
  - POSTGRES_MAX_CONNECTIONS=200
```

### Redis Memory
Edit `docker-compose.yml`:
```yaml
command: redis-server --maxmemory 512mb
```

### Nginx Caching
Edit `docker/nginx/conf.d/default.conf`:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale web containers
docker-compose up -d --scale web=3

# Requires load balancer (Nginx, HAProxy)
```

### Separate Database Server
```yaml
# In docker-compose.yml
services:
  db:
    # Remove this service
    
  web:
    environment:
      - DB_HOST=external-db-host.com
```

## 🔒 Security Checklist

- [ ] Change default passwords
- [ ] Set strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL/HTTPS
- [ ] Configure firewall (UFW)
- [ ] Regular backups
- [ ] Update containers regularly
- [ ] Monitor logs
- [ ] Use secrets management

## 📚 Additional Resources

- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **Django Deployment:** https://docs.djangoproject.com/en/5.2/howto/deployment/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Nginx:** https://nginx.org/en/docs/

## 🆘 Support

For issues:
1. Check logs: `make logs`
2. Verify health: `make health`
3. Review documentation
4. Check GitHub issues

## 📝 Development Workflow

```bash
# Start development environment
make up-dev

# Make changes to code (auto-reload enabled)

# Run tests
make test

# Check migrations
make makemigrations

# Apply migrations
make migrate

# Stop when done
make down
```

## 🎉 Success!

Your Fikrly platform is now running in Docker containers with:
- ✅ Auto-healing (health checks)
- ✅ Persistent data (volumes)
- ✅ Scalable architecture
- ✅ Production-ready configuration
- ✅ Automated backups
- ✅ Easy deployment

**Next:** Visit http://localhost and start using Fikrly!
