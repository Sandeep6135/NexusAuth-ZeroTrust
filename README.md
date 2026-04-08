# NexusAuth ZT

Centralized Zero Trust Identity and Access Management built on Keycloak + PostgreSQL, with a Flask target app for OIDC login validation and JWT claim inspection.

## What This Project Delivers

- Centralized authentication with Keycloak realm provisioning
- OIDC authorization code flow for a protected Flask application
- Role-based access control foundations (Admin, Developer, Viewer)
- Event logging enabled at realm level for audit visibility
- Local, reproducible setup using Docker Compose

## Repository Structure

- [docker-compose.yml](docker-compose.yml): Keycloak + PostgreSQL local stack
- [scripts/kcadm_provision.sh](scripts/kcadm_provision.sh): Automated realm/client/role/event setup via Keycloak Admin CLI
- [target-app/app.py](target-app/app.py): Flask app with SSO login, callback handling, and JWT claim inspection endpoint
- [target-app/requirements.txt](target-app/requirements.txt): Python dependencies for Flask target app
- [ARCHITECTURE.md](ARCHITECTURE.md): Expanded architecture and security model notes
- [DEPLOYMENT_AND_TESTING.md](DEPLOYMENT_AND_TESTING.md): Extended deployment/testing evidence and operational checks

## Prerequisites

- Docker Desktop (with Compose support)
- Python 3.9+ for running the Flask target app
- Bash-compatible shell for provisioning script (Git Bash/WSL/macOS/Linux)

## Quick Start

### 1) Start IAM infrastructure

```bash
docker compose up -d
```

Wait until containers are healthy:

```bash
docker compose ps
```

### 2) Provision Keycloak realm, client, roles, and events

```bash
bash scripts/kcadm_provision.sh
```

What this script provisions:

- Realm: `Infotact`
- OIDC client: `flask-target-app`
- Realm roles: `Admin`, `Developer`, `Viewer`
- Event config: user/admin events with `jboss-logging` listener

### 3) Run the Flask target app

```bash
cd target-app
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app runs at `http://localhost:5000`.

## Configure Client Secret (Required)

The Flask app currently contains a placeholder in [target-app/app.py](target-app/app.py) for `CLIENT_SECRET`.

Before end-to-end SSO works, replace it with the real secret for client `flask-target-app` from Keycloak Admin Console:

1. Open `http://localhost:8080`
2. Sign in with admin credentials from [docker-compose.yml](docker-compose.yml)
3. Go to `Infotact` -> Clients -> `flask-target-app` -> Credentials
4. Copy the client secret and update `CLIENT_SECRET` in [target-app/app.py](target-app/app.py)

## Verify the Flow

1. Open `http://localhost:5000`
2. Click login and authenticate through Keycloak
3. After redirect, visit `http://localhost:5000/verify-claims`
4. Confirm JWT payload and role claims are returned

## Default Local Endpoints

- Keycloak: `http://localhost:8080`
- Flask target app: `http://localhost:5000`
- PostgreSQL: `localhost:5432`

## Security Notes

- This setup is development-oriented (`start-dev` Keycloak mode).
- Credentials in [docker-compose.yml](docker-compose.yml) are sample/local only.
- Flask `app.secret_key` in [target-app/app.py](target-app/app.py) should be environment-driven in production.
- Do not commit real client secrets or production credentials.

## Useful Commands

Start services:

```bash
docker compose up -d
```

Stop services:

```bash
docker compose down
```

View Keycloak logs:

```bash
docker compose logs -f keycloak
```

## Troubleshooting

- Provisioning script fails on Windows terminal:
	- Run it from Git Bash or WSL because [scripts/kcadm_provision.sh](scripts/kcadm_provision.sh) is a Bash script.
- Login redirects but callback fails:
	- Verify `CLIENT_SECRET` is updated in [target-app/app.py](target-app/app.py).
- Realm/client already exists errors:
	- This can happen on repeated provisioning runs; reset containers/volumes if you want a clean rebuild.

## Extended Documentation

- Detailed architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Full deployment and testing evidence: [DEPLOYMENT_AND_TESTING.md](DEPLOYMENT_AND_TESTING.md)

## License

This repository is for internship/project demonstration purposes.