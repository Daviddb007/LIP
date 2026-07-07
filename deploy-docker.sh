#!/bin/bash
# Laboratorio de Inteligencia Pública - Docker Deployment Script
# Run this on the production server (165.22.179.8)

set -e

echo "=========================================="
echo "  LABORATORIO DE INTELIGENCIA PÚBLICA - DOCKER DEPLOY"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Install Docker
echo -e "\n${YELLOW}[1/7] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "\n${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}Docker version: $(docker --version)${NC}"
echo -e "${GREEN}Docker Compose version: $(docker-compose --version)${NC}"

# Step 2: Clone repository
echo -e "\n${YELLOW}[2/7] Setting up application...${NC}"
cd /var/www

if [ ! -d "l-inteligenciapublica" ]; then
    git clone https://github.com/Daviddb007/Construyamos_Colombia.git l-inteligenciapublica
fi

cd l-inteligenciapublica

# Step 3: Create .env file
echo -e "\n${YELLOW}[3/7] Creating environment file...${NC}"
if [ ! -f .env ]; then
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    
    # Generate secure password
    ADMIN_PASS_ORIG=$(openssl rand -base64 12)
    ADMIN_PASS_HASH=$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('${ADMIN_PASS_ORIG}', method='pbkdf2:sha256', salt_length=16))" 2>/dev/null || echo "CHANGE_ME")
    
    # Database password
    DB_PASS=$(openssl rand -base64 16)
    
    cat > .env << EOF
# Application
FLASK_CONFIG=production
SECRET_KEY=${SECRET_KEY}
ADMIN_USER=admin
ADMIN_PASS=${ADMIN_PASS_HASH}
PORT=8000
LOG_LEVEL=info

# Database
DB_USER=construyamos
DB_PASSWORD=${DB_PASS}
DB_NAME=construyamos_colombia
DATABASE_URL=postgresql://construyamos:${DB_PASS}@db:5432/construyamos_colombia

# Redis
RATELIMIT_STORAGE_URI=redis://redis:6379/0
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=redis://redis:6379/1
EOF

    echo -e "${GREEN}=========================================="
    echo "  CREDENTIALS (SAVE THESE!)"
    echo "=========================================="
    echo "SECRET_KEY: ${SECRET_KEY}"
    echo "ADMIN_USER: admin"
    echo "ADMIN_PASS: ${ADMIN_PASS_ORIG}"
    echo "DB_PASSWORD: ${DB_PASS}"
    echo "==========================================${NC}"
fi

# Step 4: Create nginx SSL directory
echo -e "\n${YELLOW}[4/7] Setting up SSL...${NC}"
mkdir -p nginx/ssl

# Generate self-signed certificate (replace with Let's Encrypt later)
if [ ! -f nginx/ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=CO/ST=Bogota/L=Bogota/O=InteligenciaPublica/CN=l-inteligenciapublica.stonelytics.tech"
fi

# Step 5: Build and start containers
echo -e "\n${YELLOW}[5/7] Building Docker containers...${NC}"
docker-compose build --no-cache

echo -e "\n${YELLOW}[6/7] Starting services...${NC}"
docker-compose up -d

# Step 6: Wait for services
echo -e "\n${YELLOW}[7/7] Waiting for services to start...${NC}"
sleep 10

# Run migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
docker-compose exec app flask db upgrade

# Seed database
echo -e "${YELLOW}Seeding database...${NC}"
docker-compose exec app flask seed

# Final verification
echo -e "\n${GREEN}=========================================="
echo "  DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Container status:"
docker-compose ps
echo ""
echo "Health check:"
docker-compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
echo ""
echo "Application URL: https://l-inteligenciapublica.stonelytics.tech"
echo "=========================================="
