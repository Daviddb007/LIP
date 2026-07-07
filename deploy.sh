#!/bin/bash
# Laboratorio de Inteligencia Pública - Production Deployment Script
# Run this script on the production server

set -e

echo "=========================================="
echo "  LABORATORIO DE INTELIGENCIA PÚBLICA - DEPLOY SCRIPT"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
APP_NAME="l_inteligenciapublica"
APP_USER="www-data"
APP_DIR="/var/www/$APP_NAME"
PYTHON_VERSION="python3"

# Step 1: System Update
echo -e "\n${YELLOW}[1/10] Updating system...${NC}"
apt update && apt upgrade -y

# Step 2: Install dependencies
echo -e "\n${YELLOW}[2/10] Installing system dependencies...${NC}"
apt install -y \
    $PYTHON_VERSION \
    $PYTHON_VERSION-pip \
    $PYTHON_VERSION-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    redis-server \
    git

# Step 3: Enable services
echo -e "\n${YELLOW}[3/10] Enabling services...${NC}"
systemctl enable postgresql redis-server nginx
systemctl start postgresql redis-server

# Step 4: Configure PostgreSQL
echo -e "\n${YELLOW}[4/10] Configuring PostgreSQL...${NC}"
echo -e "${GREEN}Please enter PostgreSQL password for user 'construyamos':${NC}"
read -s DB_PASSWORD

sudo -u postgres psql -c "CREATE USER construyamos WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE construyamos_colombia OWNER construyamos;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE construyamos_colombia TO construyamos;"

# Step 5: Clone and setup app
echo -e "\n${YELLOW}[5/10] Setting up application...${NC}"
mkdir -p /var/www
cd /var/www

if [ ! -d "$APP_DIR" ]; then
    git clone <YOUR_REPOSITORY_URL> $APP_DIR
fi

cd $APP_DIR

# Step 6: Python environment
echo -e "\n${YELLOW}[6/10] Creating Python environment...${NC}"
$PYTHON_VERSION -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 7: Configure environment
echo -e "\n${YELLOW}[7/10] Configuring environment...${NC}"
if [ ! -f .env ]; then
    cp .env.production .env
    # Update database URL with the password
    sed -i "s/tu-password-de-postgres/$DB_PASSWORD/g" .env
    echo -e "${GREEN}Environment file created. Please review .env if needed.${NC}"
fi

# Step 8: Database migrations
echo -e "\n${YELLOW}[8/10] Running database migrations...${NC}"
flask db upgrade

# Step 9: Seed database (first time only)
echo -e "\n${YELLOW}[9/10] Seeding database...${NC}"
read -p "Seed database with initial data? (y/n) " SEED
if [ "$SEED" = "y" ]; then
    flask seed
fi

# Step 10: Configure systemd service
echo -e "\n${YELLOW}[10/10] Configuring systemd service...${NC}"
cat > /etc/systemd/system/inteligenciapublica.service << EOF
[Unit]
Description=Laboratorio de Inteligencia Pública Flask App
After=network.target postgresql.service redis.service

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py run:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable inteligenciapublica
systemctl start inteligenciapublica

# Configure Nginx
echo -e "\n${YELLOW}Configuring Nginx...${NC}"
read -p "Enter domain name (e.g., inteligenciapublica.stonelytics.tech): " DOMAIN

cat > /etc/nginx/sites-available/inteligenciapublica << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_DIR/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/inteligenciapublica /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

# SSL Certificate
echo -e "\n${YELLOW}Setting up SSL certificate...${NC}"
read -p "Setup SSL with Certbot? (y/n) " SSL
if [ "$SSL" = "y" ]; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# Firewall
echo -e "\n${YELLOW}Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Final verification
echo -e "\n${GREEN}=========================================="
echo "  DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Service status:"
systemctl status construyamos --no-pager
echo ""
echo "Health check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo "Application URL: http://$DOMAIN"
echo "=========================================="
