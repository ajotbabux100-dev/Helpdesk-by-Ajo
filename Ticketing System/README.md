# Helpdesk & Ticketing System

> A full-stack internal helpdesk portal built for **GSH & ISH OMAN** — submit tickets, track SLAs, manage users, and audit everything in one place.

![Version](https://img.shields.io/badge/version-1.0.16-blue)
![Django](https://img.shields.io/badge/Django-6.0.6-green)
![Next.js](https://img.shields.io/badge/Next.js-15.3.4-black)
![License](https://img.shields.io/badge/license-Private-red)

---

## Features

| Area | Details |
|---|---|
| **Ticketing** | Create, assign, escalate, resolve, and reopen tickets with full comment threads and @mentions |
| **SLA Management** | Per-department SLA policies (Critical / High / Medium / Low) with live breach timers and dashboard alerts |
| **Departments** | Department management with SLA policy CRUD via admin UI |
| **Users & Roles** | End User · Agent · Manager · Admin — role-based access throughout |
| **Audit Log** | Every action logged with user, IP, timestamp, old/new values |
| **Login History** | Per-user login/logout event log with IP address, visible in the Users tab |
| **Notifications** | In-app notification bell with unread count; email notifications via SMTP |
| **Reports** | Dashboard summary, ticket trends, department breakdowns |
| **Branding** | Customisable portal name, company name, logo, primary colour, welcome text, support hours |
| **Email** | Microsoft 365 / SMTP configurable — ticket updates, assignments, SLA breach alerts |
| **Security** | JWT auth with refresh rotation, XSS/clickjacking headers, brute-force resistant, full audit trail |
| **Performance** | SQLite WAL mode, connection pooling, in-memory branding cache, Next.js production mode |

---

## Tech Stack

### Backend
- **Django 6.0.6** + Django REST Framework
- **SimpleJWT** — access + refresh token auth with blacklisting
- **SQLite** (default) or **PostgreSQL** (configurable)
- **Whitenoise** — static file serving
- **Waitress** — production WSGI server (Windows-compatible)
- **python-decouple** — environment variable management

### Frontend
- **Next.js 15.3.4** (App Router) + **React 19**
- **TypeScript**
- **Tailwind CSS** + **tw-animate-css**
- **Framer Motion** — micro-interactions (button press, modal spring, card hover)
- **Recharts** — status breakdown donut chart on dashboard
- **Zustand v5** — auth state with persistence
- **Lucide React** — icons

### Infrastructure
- **PM2** — process manager with auto-restart for both Django and Next.js
- **Git pre-commit hook** — auto-increments version on every commit

---

## Project Structure

```
Ticketing System/
├── backend/                  # Django project
│   ├── audit/                # Audit log app
│   ├── branding/             # Portal branding & SMTP settings
│   ├── config/               # Django settings, URLs, WSGI
│   ├── departments/          # Department + SLA policy management
│   ├── notifications/        # In-app notifications
│   ├── reports/              # Dashboard summary & reports
│   ├── tickets/              # Core ticketing app
│   ├── users/                # Custom user model & auth
│   ├── logs/                 # Rotating log files (runtime, gitignored)
│   ├── manage.py
│   └── .env                  # Environment config (gitignored)
│
├── frontend/                 # Next.js project
│   ├── app/
│   │   ├── (auth)/login/     # Login page
│   │   ├── (dashboard)/      # All authenticated pages
│   │   │   ├── dashboard/    # Bento grid dashboard
│   │   │   ├── tickets/      # Ticket list + detail + new
│   │   │   ├── departments/  # Department + SLA management
│   │   │   ├── users/        # User management + login history
│   │   │   ├── reports/      # Reports page
│   │   │   ├── audit/        # Audit log (login events excluded)
│   │   │   └── settings/     # Portal branding & email settings
│   │   ├── components/
│   │   │   ├── layout/       # Sidebar, Topbar
│   │   │   └── ui/           # Button, Modal, Card, Input, Badge...
│   │   └── lib/              # api.ts, store.ts, types.ts, utils.ts
│   ├── next.config.ts        # Reads version.json at build time
│   └── .env.local            # Frontend env (gitignored)
│
├── version.json              # Auto-incremented on every commit
├── ecosystem.config.js       # PM2 process definitions
├── start.bat                 # First-time start (migrate + build + PM2)
├── stop.bat                  # Graceful shutdown
└── deploy.bat                # Update deploy (stop + migrate + build + restart)
```

---

## Quick Start — Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1 — Clone & set up backend

```bash
git clone https://github.com/ajotbabux100-dev/Helpdesk-by-Ajo.git
cd "Helpdesk-by-Ajo/Ticketing System"

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r backend/requirements.txt
```

### 2 — Configure environment

Edit `backend/.env`:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@yourdomain.com
EMAIL_HOST_PASSWORD=your-password
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 3 — Initialise database & create superuser

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 4 — Run development servers

**Backend** (terminal 1):
```bash
cd backend
python manage.py runserver 8000
```

**Frontend** (terminal 2):
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Production Deployment — Windows Server

### One-time setup

```bash
# Install PM2 globally
npm install -g pm2

# Install production Python dependencies (already in requirements.txt)
venv\Scripts\pip install waitress whitenoise

# Collect static files
venv\Scripts\python backend\manage.py collectstatic --noinput
```

Update `backend/.env` for production:

```env
DEBUG=False
SECRET_KEY=<run: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=localhost,127.0.0.1,YOUR_SERVER_IP
CORS_ALLOWED_ORIGINS=http://YOUR_SERVER_IP:3000
FRONTEND_URL=http://YOUR_SERVER_IP:3000
```

Enable HTTPS when you have a TLS certificate:
```env
USE_HTTPS=True
```

### Start

```bash
start.bat
```

This will:
1. Run any pending migrations
2. Collect static files
3. Build the Next.js frontend (if `.next` is missing)
4. Start both services under PM2

| Service | URL |
|---|---|
| Web portal | http://localhost:3000 |
| API | http://localhost:8000/api |
| Health check | http://localhost:8000/health/ |

### PM2 commands

```bash
pm2 status               # show running processes
pm2 logs                 # live log stream (all)
pm2 logs helpdesk-api    # Django API logs only
pm2 logs helpdesk-web    # Next.js logs only
pm2 restart all          # restart both
pm2 stop all             # stop everything
```

### Deploy an update

```bash
deploy.bat
```

Stops services → applies migrations → rebuilds frontend → restarts PM2.

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | **Required.** Django secret key |
| `DEBUG` | `False` | Set `True` for development only |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated allowed frontend origins |
| `USE_HTTPS` | `False` | Enable HSTS + secure cookies (requires TLS) |
| `DB_ENGINE` | `sqlite` | `sqlite` or `postgresql` |
| `DB_NAME` | `ticketing_db` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL user |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `EMAIL_HOST` | `smtp.office365.com` | SMTP server |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_HOST_USER` | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | — | SMTP password |
| `EMAIL_USE_TLS` | `True` | Use STARTTLS |
| `DEFAULT_FROM_EMAIL` | — | Sender display name + address |
| `FRONTEND_URL` | `http://localhost:3000` | Used in email notification links |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | Access token lifetime |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | `7` | Refresh token lifetime |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Django API base URL — e.g. `http://localhost:8000/api` |

---

## User Roles

| Role | Permissions |
|---|---|
| **End User** | Submit tickets, view own tickets, add comments |
| **Agent** | View and manage assigned tickets, update status, add internal notes |
| **Manager** | All agent permissions + view all tickets, access reports and departments |
| **Admin** | Full access — users, audit log, branding, settings, SLA policies |

---

## API Endpoints

| Prefix | Description |
|---|---|
| `/api/auth/` | Login, logout, token refresh, user profile |
| `/api/tickets/` | Ticket CRUD, comments, attachments, escalation |
| `/api/departments/` | Department management + SLA policies |
| `/api/notifications/` | In-app notifications |
| `/api/audit/` | Audit log (filterable by action, user, ticket) |
| `/api/reports/` | Dashboard summary, ticket trends |
| `/api/branding/` | Portal settings and SMTP configuration |
| `/health/` | Health check — returns `{"status":"ok","db":true}` |

---

## Versioning

The project uses automatic patch versioning. A git pre-commit hook increments the patch number on every commit:

```
1.0.15  →  git commit  →  1.0.16  →  git commit  →  1.0.17
```

The current version is displayed in the bottom-left corner of the sidebar.  
`version.json` is the single source of truth — Next.js reads it at build time and bakes it into the UI.

To bump major or minor, edit `version.json` manually before committing:

```json
{ "major": 2, "minor": 0, "patch": 0, "version": "2.0.0" }
```

The next commit will then produce `v2.0.1`.

---

## Logs

Runtime logs are written to `backend/logs/` (gitignored):

| File | Contents |
|---|---|
| `django.log` | All INFO+ events, rotates at 10 MB, 5 backups |
| `errors.log` | ERROR+ only |
| `pm2-api-out.log` | Django stdout via PM2 |
| `pm2-web-error.log` | Next.js stderr via PM2 |

---

## Security Notes

- JWT access tokens expire after 60 minutes; refresh tokens rotate on every use and are blacklisted after logout
- All auth state (Zustand persisted store + localStorage keys) is fully cleared on token expiry — no stale-session redirect loops
- Security headers active in production: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, strict referrer policy
- Login/logout events are tracked in the audit log and surfaced per-user in the Users tab
- The Django browsable API is disabled in production (`JSONRenderer` only)
- Enable `USE_HTTPS=True` when deploying behind TLS to activate HSTS, secure cookies, and SSL redirect

---

## Built by

**AJO** — IT Department, GSH & ISH OMAN  
Repository: [github.com/ajotbabux100-dev/Helpdesk-by-Ajo](https://github.com/ajotbabux100-dev/Helpdesk-by-Ajo)
