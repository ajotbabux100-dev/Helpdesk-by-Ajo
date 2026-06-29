# Helpdesk & Ticketing System

A full-stack unified helpdesk portal for raising, tracking, and resolving support tickets across all departments — built with **Django REST Framework** (backend) and **Next.js 15** (frontend).

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Hardware Requirements](#hardware-requirements)
- [VPS Setup (Ubuntu 22.04 / 24.04 LTS)](#vps-setup-ubuntu-2204--2404-lts)
  - [1. System Preparation](#1-system-preparation)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. PostgreSQL Setup](#3-postgresql-setup)
  - [4. Clone the Repository](#4-clone-the-repository)
  - [5. Backend Setup](#5-backend-setup)
  - [6. Frontend Setup](#6-frontend-setup)
  - [7. Gunicorn (Backend Service)](#7-gunicorn-backend-service)
  - [8. PM2 (Frontend Service)](#8-pm2-frontend-service)
  - [9. Nginx Reverse Proxy](#9-nginx-reverse-proxy)
  - [10. SSL Certificate (HTTPS)](#10-ssl-certificate-https)
  - [11. Firewall](#11-firewall)
- [Environment Variables](#environment-variables)
- [First Login](#first-login)
- [Development Setup (Local)](#development-setup-local)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **Role-based access** — End User, Agent, Manager, Admin
- **Auto-assignment** — tickets routed to configured assignee → manager → least-busy agent
- **SLA tracking** — response & resolution deadlines with breach alerts
- **Configurable ticket form** — admin toggles which fields are required
- **Custom ticket series** — prefix, separator, digits, year format, yearly reset
- **Full branding** — logo, company name, portal name, primary colour (all from admin UI)
- **Email notifications** — ticket created, assigned, updated, resolved, commented
- **Audit log** — every action recorded with user, IP, timestamp
- **Reports & charts** — tickets by status, priority, department, trend over time, agent performance, SLA compliance
- **Comments** — public replies and internal agent notes
- **File attachments** — per ticket and per comment

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, Django 5, Django REST Framework |
| Auth | JWT (SimpleJWT) with refresh token rotation |
| Database | PostgreSQL 15+ (SQLite for dev/testing) |
| Frontend | Next.js 15, React 19, Tailwind CSS 4, Turbopack |
| State | Zustand (persisted to localStorage) |
| HTTP Client | Axios with JWT interceptors |
| Charts | Recharts |
| Process Manager | Gunicorn (backend), PM2 (frontend) |
| Web Server | Nginx (reverse proxy + static files) |
| SSL | Let's Encrypt (Certbot) |
| OS | Ubuntu 22.04 LTS / 24.04 LTS |

---

## Hardware Requirements

Sizing is based on **real-time concurrent users** (users actively submitting or viewing tickets at the same time — not registered users).

### Minimum Recommended Specs

| Concurrent Users | vCPU | RAM | Storage | Bandwidth | Notes |
|---|---|---|---|---|---|
| **10** | 1 vCPU | 1 GB | 20 GB SSD | 100 Mbps | Entry-level VPS. Suitable for small teams (< 50 staff). SQLite can be used. |
| **20** | 2 vCPU | 2 GB | 30 GB SSD | 100 Mbps | Small office. PostgreSQL recommended. 2 Gunicorn workers. |
| **30** | 2 vCPU | 4 GB | 40 GB SSD | 200 Mbps | Mid-size team. 4 Gunicorn workers. Enable Nginx caching. |
| **100** | 4 vCPU | 8 GB | 80 GB SSD | 500 Mbps | Department-scale. 8 Gunicorn workers. Redis for caching recommended. |
| **1000** | 8–16 vCPU | 32 GB | 200 GB SSD | 1 Gbps | Enterprise. Separate DB server, Redis, load balancer, multiple app nodes. |

### Detailed Breakdown

#### 10 Concurrent Users — Entry VPS
```
CPU:      1 vCPU (any cloud provider micro/nano tier)
RAM:      1 GB (512 MB minimum — tight)
Disk:     20 GB SSD
Network:  100 Mbps
Database: SQLite (acceptable) or PostgreSQL on same server
Workers:  2 Gunicorn workers
Example:  DigitalOcean Droplet $6/mo, Hetzner CX11, AWS t3.micro
```

#### 20 Concurrent Users — Small Office
```
CPU:      2 vCPU
RAM:      2 GB
Disk:     30 GB SSD
Network:  100 Mbps
Database: PostgreSQL (same server)
Workers:  2–4 Gunicorn workers  (formula: 2 × vCPU + 1)
Example:  DigitalOcean $12/mo, Hetzner CX21, AWS t3.small
```

#### 30 Concurrent Users — Mid-size Team
```
CPU:      2–4 vCPU
RAM:      4 GB
Disk:     40 GB SSD
Network:  200 Mbps
Database: PostgreSQL (same server or dedicated DB droplet)
Workers:  4–6 Gunicorn workers
Cache:    Nginx static file caching
Example:  DigitalOcean $24/mo, Hetzner CX31, AWS t3.medium
```

#### 100 Concurrent Users — Departmental
```
CPU:      4–8 vCPU
RAM:      8–16 GB
Disk:     80 GB SSD
Network:  500 Mbps
Database: PostgreSQL on dedicated server (recommended)
Workers:  8–16 Gunicorn workers
Cache:    Redis for session + API response caching
CDN:      Recommended for static assets
Example:  DigitalOcean $48–96/mo, Hetzner CX41, AWS t3.xlarge
```

#### 1000 Concurrent Users — Enterprise
```
CPU:      8–16 vCPU (app) + 4–8 vCPU (DB)
RAM:      32 GB (app) + 16 GB (DB)
Disk:     200 GB NVMe SSD (app) + 500 GB (DB with replication)
Network:  1 Gbps
Architecture:
  - Load balancer (Nginx or HAProxy) → 2–4 app servers
  - Dedicated PostgreSQL primary + read replica
  - Redis cluster for caching & sessions
  - S3-compatible object storage for attachments
  - CDN (Cloudflare) for frontend static files
Example:  DigitalOcean managed Kubernetes or dedicated servers
          AWS: Application Load Balancer + ECS + RDS PostgreSQL
```

> **Rule of thumb:** Each Gunicorn worker consumes ~80–150 MB RAM. Each PostgreSQL connection ~5–10 MB. Budget accordingly.

---

## VPS Setup (Ubuntu 22.04 / 24.04 LTS)

All commands run as **root** or with `sudo`. Replace `your-domain.com` and `your_*` placeholders throughout.

---

### 1. System Preparation

```bash
apt update && apt upgrade -y
apt install -y curl wget git unzip build-essential software-properties-common
timedatectl set-timezone Asia/Muscat   # adjust to your timezone
```

---

### 2. Install Dependencies

#### Python 3.11+
```bash
add-apt-repository ppa:deadsnakes/ppa -y
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
python3.11 --version   # confirm
```

#### Node.js 20 LTS
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
node --version    # confirm v20.x
npm install -g pm2
```

#### PostgreSQL 15
```bash
apt install -y postgresql postgresql-contrib
systemctl enable --now postgresql
```

#### Nginx
```bash
apt install -y nginx
systemctl enable --now nginx
```

---

### 3. PostgreSQL Setup

```bash
sudo -u postgres psql <<EOF
CREATE USER helpdesk_user WITH PASSWORD 'StrongPassword123!';
CREATE DATABASE helpdesk_db OWNER helpdesk_user;
GRANT ALL PRIVILEGES ON DATABASE helpdesk_db TO helpdesk_user;
EOF
```

---

### 4. Clone the Repository

```bash
cd /var/www
git clone https://github.com/itgshoman1-prog/Helpdesk-Ticket.git helpdesk
cd helpdesk
```

---

### 5. Backend Setup

```bash
cd /var/www/helpdesk/"Ticketing System"/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary   # production extras
```

#### Create `.env` file
```bash
cat > .env <<EOF
SECRET_KEY=replace-with-a-long-random-string-at-least-50-chars
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP

DB_ENGINE=postgresql
DB_NAME=helpdesk_db
DB_USER=helpdesk_user
DB_PASSWORD=StrongPassword123!
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=helpdesk@your-domain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=Helpdesk <helpdesk@your-domain.com>

CORS_ALLOWED_ORIGINS=https://your-domain.com
EOF
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(60))"
```

#### Run migrations and seed
```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser --email admin@your-domain.com
python manage.py collectstatic --noinput
```

#### Set permissions
```bash
chown -R www-data:www-data /var/www/helpdesk
chmod -R 755 /var/www/helpdesk
```

---

### 6. Frontend Setup

```bash
cd /var/www/helpdesk/"Ticketing System"/frontend

# Install dependencies
npm install

# Create environment file
cat > .env.production <<EOF
NEXT_PUBLIC_API_URL=https://your-domain.com/api
EOF

# Build for production
npm run build
```

---

### 7. Gunicorn (Backend Service)

Scale workers using the formula: **workers = (2 × vCPU) + 1**

```bash
cat > /etc/systemd/system/helpdesk-backend.service <<EOF
[Unit]
Description=Helpdesk Django Backend
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/helpdesk/Ticketing System/backend
Environment="PATH=/var/www/helpdesk/Ticketing System/backend/venv/bin"
ExecStart=/var/www/helpdesk/Ticketing System/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --bind unix:/run/helpdesk-backend.sock \
    --access-logfile /var/log/helpdesk/gunicorn-access.log \
    --error-logfile /var/log/helpdesk/gunicorn-error.log \
    config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/log/helpdesk
chown www-data:www-data /var/log/helpdesk

systemctl daemon-reload
systemctl enable --now helpdesk-backend
systemctl status helpdesk-backend
```

Worker counts by load:

| Concurrent Users | `--workers` value |
|---|---|
| 10 | 2 |
| 20 | 4 |
| 30 | 4–6 |
| 100 | 8–16 |
| 1000 | Scale horizontally — multiple servers |

---

### 8. PM2 (Frontend Service)

```bash
cd "/var/www/helpdesk/Ticketing System/frontend"

pm2 start npm --name "helpdesk-frontend" -- start
pm2 save
pm2 startup systemd -u www-data --hp /var/www
```

The frontend runs on port **3000** by default. Nginx proxies to it.

---

### 9. Nginx Reverse Proxy

```bash
cat > /etc/nginx/sites-available/helpdesk <<'EOF'
upstream django_backend {
    server unix:/run/helpdesk-backend.sock fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP → HTTPS (filled in after certbot)
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL — filled in by certbot
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 20M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Django static files
    location /static/ {
        alias /var/www/helpdesk/Ticketing\ System/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Django media files (uploads / logos)
    location /media/ {
        alias /var/www/helpdesk/Ticketing\ System/backend/media/;
        expires 7d;
    }

    # Django API
    location /api/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://django_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js frontend (everything else)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/helpdesk /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

---

### 10. SSL Certificate (HTTPS)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com -d www.your-domain.com
# Follow prompts — select option to redirect HTTP → HTTPS

# Auto-renewal (already set up by certbot, verify with):
systemctl status certbot.timer
```

---

### 11. Firewall

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

Only ports 22 (SSH), 80 (HTTP→redirect), and 443 (HTTPS) should be open externally. PostgreSQL (5432) and Next.js (3000) are internal only.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key — keep private | 60+ char random string |
| `DEBUG` | Set to `False` in production | `False` |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `your-domain.com,www.your-domain.com` |
| `DB_ENGINE` | `postgresql` or `sqlite` | `postgresql` |
| `DB_NAME` | PostgreSQL database name | `helpdesk_db` |
| `DB_USER` | PostgreSQL username | `helpdesk_user` |
| `DB_PASSWORD` | PostgreSQL password | `StrongPassword123!` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_HOST` | SMTP server | `smtp.office365.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username | `helpdesk@domain.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password | — |
| `CORS_ALLOWED_ORIGINS` | Frontend origin | `https://your-domain.com` |

### Frontend (`frontend/.env.production`)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Django API base URL | `https://your-domain.com/api` |

---

## First Login

After setup, the superuser you created with `createsuperuser` can log in at:

```
https://your-domain.com/login
```

Default seeded admin (development only):
```
Email:    admin@helpdesk.local
Password: Admin@1234
```

**Change this immediately in production.**

Go to **Settings → Organisation** to configure your company name, logo, and branding.

---

## Development Setup (Local)

```bash
git clone https://github.com/itgshoman1-prog/Helpdesk-Ticket.git
cd "Helpdesk-Ticket/Ticketing System"
```

### Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env        # edit as needed — DB_ENGINE=sqlite works out of the box
python manage.py migrate
python manage.py runserver 8000
```

### Frontend
```bash
cd frontend
npm install
# Create frontend/.env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev      # Turbopack — visit http://localhost:3000
```

---

## Project Structure

```
Ticketing System/
├── backend/
│   ├── audit/              # Audit log — every user action recorded
│   ├── branding/           # SystemSettings: logo, colours, ticket series, email config
│   ├── config/             # Django project settings and URL routing
│   ├── departments/        # Departments, SLA policies, auto-assign config
│   ├── notifications/      # Email notifications for all ticket events
│   ├── reports/            # Dashboard summary, charts, SLA compliance
│   ├── tickets/            # Tickets, comments, attachments, auto-assign logic
│   ├── users/              # Custom user model, JWT auth, roles
│   ├── templates/emails/   # HTML email templates
│   ├── requirements.txt
│   └── manage.py
│
└── frontend/
    └── app/
        ├── (auth)/login/           # Login page
        ├── (dashboard)/
        │   ├── dashboard/          # Home dashboard
        │   ├── tickets/            # Ticket list + new + detail
        │   ├── departments/        # Department management
        │   ├── users/              # User management
        │   ├── reports/            # Charts and analytics
        │   ├── audit/              # Audit log viewer
        │   └── settings/           # System settings (branding, series, form fields)
        ├── components/
        │   ├── layout/             # Sidebar, Topbar
        │   └── ui/                 # Button, Input, Select, Card, Modal, Badge, Textarea
        └── lib/
            ├── api.ts              # Axios with JWT interceptors
            ├── store.ts            # Zustand auth store
            ├── types.ts            # TypeScript interfaces
            └── utils.ts            # Date formatting, class helpers
```

---

## Keeping the System Updated

```bash
cd /var/www/helpdesk
git pull origin main

# Backend
cd "Ticketing System/backend"
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart helpdesk-backend

# Frontend
cd ../frontend
npm install
npm run build
pm2 restart helpdesk-frontend
```

---

## License

MIT — free to use, modify, and distribute.

---

*Built for GSH & ISH OMAN — Unified Helpdesk & Ticketing System*
