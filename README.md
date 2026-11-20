# Task Manager API — practice project

Read `PRD.md` first. This project is designed for learning; do not use it as-is for a production system.

## 1. Create and activate a virtual environment (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 3. Configure environment variables

Copy `.env.example` to `.env`, then replace the JWT secret and admin password with your own strong values.

PowerShell:
```powershell
Copy-Item .env.example .env
```

For local development, load `.env` variables into the current PowerShell session before running:
```powershell
$env:JWT_SECRET="paste-a-long-random-secret-here"
$env:ADMIN_EMAIL="admin@example.com"
$env:ADMIN_PASSWORD="use-a-strong-password-here"
$env:ADMIN_NAME="Project Admin"
```

The application reads environment variables from the process. The `.env` file is automatically read by Docker Compose through `env_file`; plain `uvicorn` does not automatically load it.

## 4. Run the API locally

```powershell
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/

## 5. Test in Swagger

1. `POST /auth/register` — create a normal user.
2. `POST /auth/login` — copy `access_token` from the response.
3. Click **Authorize** in Swagger and enter the token as `Bearer <token>` if the UI requests the full value. With HTTP Bearer, Swagger may provide a token-only field; follow the displayed prompt.
4. Call `GET /auth/me`.
5. Create and list tasks using `/tasks`.
6. To test admin routes, configure `ADMIN_EMAIL` and `ADMIN_PASSWORD` before starting the app, then log in as that admin.

## 6. Docker

Build:
```powershell
docker build -t task-manager-api:local .
```

Run for a quick test (database stored in a named volume):
```powershell
docker volume create task-manager-data
docker run -d --name task-manager-api -p 8000:8000 --env-file .env -e DATABASE_URL=sqlite:////data/task_manager.db -v task-manager-data:/data task-manager-api:local
```

Check:
```powershell
docker ps
docker logs task-manager-api
```

Stop/remove the container:
```powershell
docker stop task-manager-api
docker rm task-manager-api
```

The named volume remains after container removal, preserving the SQLite database.

## Notes
- `JWT_SECRET` must be set before starting the API.
- Never commit `.env`, credentials, private keys, or real secrets.
- For a real deployment, use HTTPS, managed secrets, database migrations, backups, and a production database.
- For CI/CD, publish immutable tags (for example, the Git commit SHA) and keep a known-good tag for rollback.
