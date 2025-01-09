#!/bin/bash

set -e

# Step 1: Request domain name and server IP from the user
echo "Please enter your domain name (e.g., example.com):"
read DOMAIN_NAME
echo "Please enter your server IP address (e.g., 192.168.1.1):"
read SERVER_IP
echo "Please enter custom Apache port:"
read APACHE_PORT
echo "Please enter custom SSH port:"
read SSH_PORT

NGINX_CONF="./kalinuxv1/kalinuxsec/kalinux_security/static/public/download/tools/nginx/nginx.conf"
APACHE_CONF="./kalinuxv1/kalinuxsec/kalinux_security/static/public/download/tools/apache2/sites-available/kalidev.conf"

sed -i "s|<DOMAIN_NAME>|$DOMAIN_NAME|g" $NGINX_CONF
sed -i "s|<SERVER_IP>|$SERVER_IP|g" $NGINX_CONF
sed -i "s|<DOMAIN_NAME>|$DOMAIN_NAME|g" $APACHE_CONF
sed -i "s|<SERVER_IP>|$SERVER_IP|g" $APACHE_CONF

# Step 3: Update system and install dependencies
echo "Updating system and installing dependencies..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common \
  gnupg2 \
  unzip \
  git \
  clamav \
  chkrootkit \
  rkhunter \
  lynis \
  iptables \
  ipset \
  fail2ban \
  nginx \
  apache2 \
  python3 \
  python3-pip \
  python3-venv \
  certbot \
  python3-certbot-nginx

# Step 4: Install Docker and Docker Compose
echo "Installing Docker and Docker Compose..."
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker --version
docker-compose --version

# Step 5: Build and start Docker containers
echo "Building and starting Docker containers..."
sudo docker-compose up --build -d

# Step 6: Configure Nginx and Apache
echo "Setting up Nginx and Apache configurations..."
openssl dhparam -out /etc/ssl/nginx-dhparam.pem 2048

sudo cp $NGINX_CONF /etc/nginx/conf.d/kalidev.conf
sudo systemctl restart nginx

sudo cp $APACHE_CONF /etc/apache2/sites-available/kalidev.conf
sudo ln -s /etc/apache2/sites-available/kalidev.conf /etc/apache2/sites-enabled/
sudo systemctl restart apache2

# Step 7: Set up Gunicorn service
echo "Setting up Gunicorn service..."
sudo cp ./kalinuxv1/tools/flaskapp.service /etc/systemd/system/flaskapp.service
sudo systemctl daemon-reload
sudo systemctl enable flaskapp.service
sudo systemctl start flaskapp.service

# Step 8: Enable Fail2Ban
echo "Configuring Fail2Ban..."
sudo cp ./kalinuxv1/kalinuxsec/kalinux_security/static/public/download/tools/fail2ban/jail.local /etc/fail2ban/jail.local
sudo systemctl restart fail2ban

# Step 9: Finalize installation
echo "Cleaning up temporary files..."
rm -rf ./kalinuxv1.zip

echo "Deployment completed successfully! Access your application via https://$DOMAIN_NAME or https://$SERVER_IP."