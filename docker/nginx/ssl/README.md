# SSL Certificate Setup for fikrly.uz

This directory should contain your SSL certificates for HTTPS.

## Option 1: Let's Encrypt (Recommended - Free)

### Using Certbot

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Stop Docker containers temporarily
make down

# Get certificate for fikrly.uz
sudo certbot certonly --standalone -d fikrly.uz -d www.fikrly.uz

# Copy certificates to docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/fikrly.uz/fullchain.pem ./docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/fikrly.uz/privkey.pem ./docker/nginx/ssl/
sudo chown $USER:$USER ./docker/nginx/ssl/*.pem

# Restart containers
make up
```

### Auto-renewal

```bash
# Add to crontab
0 0 * * * certbot renew --quiet && cp /etc/letsencrypt/live/fikrly.uz/*.pem /path/to/project/docker/nginx/ssl/ && docker-compose restart nginx
```

## Option 2: Manual Certificate

If you have certificates from another provider:

```bash
# Place your certificates here:
# - fullchain.pem (certificate + intermediate certificates)
# - privkey.pem (private key)

# Set proper permissions
chmod 644 fullchain.pem
chmod 600 privkey.pem
```

## Update Nginx Configuration

After placing certificates, update [docker/nginx/conf.d/default.conf](../conf.d/default.conf):

```nginx
server {
    listen 443 ssl http2;
    server_name fikrly.uz www.fikrly.uz;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... rest of config
}
```

## Testing

```bash
# Check SSL configuration
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx

# Test HTTPS
curl -I https://fikrly.uz
```

## Security Best Practices

- Keep private keys secure (never commit to git)
- Renew certificates before expiration (Let's Encrypt: 90 days)
- Use strong SSL configuration (see nginx config)
- Enable HSTS headers
- Test with SSL Labs: https://www.ssllabs.com/ssltest/

## Current Status

⚠️ **No certificates found** - This is normal for initial setup.

Follow Option 1 above to get free SSL certificates from Let's Encrypt.
