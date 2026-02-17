## Makefile: safe docker operations for Fikrly

.PHONY: restart rebuild build logs ps prune

restart:
	docker-compose down
	docker-compose up -d --build

rebuild:
	docker-compose build --no-cache
	docker-compose up -d

build:
	docker-compose build

logs:
	docker-compose logs -f

ps:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

prune:
	# Remove unused images; does NOT remove volumes
	docker image prune -f
# Makefile for Fikrly Docker operations

.PHONY: help build up down restart logs shell test migrate makemigrations collectstatic superuser backup restore clean

help:
	@echo "Fikrly Docker Commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all containers"
	@echo "  make up-dev         - Start in development mode"
	@echo "  make down           - Stop all containers"
	@echo "  make restart        - Restart all containers"
	@echo "  make logs           - View container logs"
	@echo "  make shell          - Open Django shell"
	@echo "  make bash           - Open bash in web container"
	@echo "  make test           - Run tests"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make collectstatic  - Collect static files"
	@echo "  make superuser      - Create superuser"
	@echo "  make backup         - Backup database and media"
	@echo "  make restore        - Restore from backup"
	@echo "  make clean          - Clean all containers and volumes"
	@echo "  make ps             - Show running containers"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Fikrly is running!"
	@echo "🌐 Access at: http://localhost"
	@echo "👨‍💼 Admin: http://localhost/admin/"
	@echo "🏥 Health: http://localhost/health/"

up-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
	@echo "✅ Fikrly is running in DEVELOPMENT mode!"
	@echo "🌐 Access at: http://localhost:8000"
	@echo "🔧 Silk profiler: http://localhost:8000/silk/"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-nginx:
	docker-compose logs -f nginx

logs-db:
	docker-compose logs -f db

shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

test:
	docker-compose exec web python manage.py test

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

superuser:
	docker-compose exec web python manage.py createsuperuser

backup:
	chmod +x docker/scripts/backup.sh
	./docker/scripts/backup.sh

restore:
	chmod +x docker/scripts/restore.sh
	./docker/scripts/restore.sh

clean:
	docker-compose down -v
	@echo "⚠️  All containers and volumes removed!"

ps:
	docker-compose ps

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Database operations
db-shell:
	docker-compose exec db psql -U fikrly_user -d fikrly_db

db-reset:
	docker-compose down -v
	docker-compose up -d db
	sleep 5
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py createsuperuser

# Production deployment
deploy-prod:
	git pull origin main
	docker-compose build
	docker-compose down
	docker-compose up -d
	docker-compose exec web python manage.py migrate --noinput
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "✅ Production deployment complete!"

# Check health
health:
	@curl -s http://localhost/health/ | python -m json.tool || echo "❌ Service not responding"
