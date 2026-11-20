# Product Requirements Document (PRD)
## Project: Task Manager API

### 1. Purpose
Build a small REST API that lets registered users create and manage their own tasks. The API will be used to practise backend development, Docker, Docker Hub, AWS EC2, and GitHub Actions CI/CD.

### 2. Users and roles
- **User:** can register, log in, create tasks, view their own tasks, update their own tasks, and delete their own tasks.
- **Admin:** can view all registered users and all tasks.

New registrations must always receive the `user` role. An administrator account is created only from environment variables; users cannot make themselves admins through the registration endpoint.

### 3. Functional requirements
1. Register with name, email, and password.
2. Log in with email and password and receive a JWT access token.
3. Use the token to access protected endpoints.
4. Create a task with title and optional description.
5. List only the signed-in user's tasks.
6. View one of the signed-in user's tasks.
7. Update one of the signed-in user's tasks.
8. Delete one of the signed-in user's tasks.
9. Admin can list all users and all tasks.

### 4. API endpoints
| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Public | Create a user account |
| POST | `/auth/login` | Public | Verify credentials and return JWT |
| GET | `/auth/me` | Logged-in user | Return current user's profile |
| POST | `/tasks` | Logged-in user | Create a task |
| GET | `/tasks` | Logged-in user | List current user's tasks |
| GET | `/tasks/{task_id}` | Owner or admin | Get one task |
| PUT | `/tasks/{task_id}` | Owner or admin | Update one task |
| DELETE | `/tasks/{task_id}` | Owner or admin | Delete one task |
| GET | `/admin/users` | Admin only | List users |
| GET | `/admin/tasks` | Admin only | List all tasks |

### 5. Security requirements
- Passwords must never be stored in plain text; use Argon2 password hashing.
- Login returns a signed JWT. Protected routes require `Authorization: Bearer <token>`.
- JWT signing key must be supplied through an environment variable and must not be committed to Git.
- Registration must not accept a role field; new users are always regular users.
- Users may access only their own tasks, unless they are an admin.
- Return appropriate HTTP errors for invalid credentials, missing records, and insufficient permissions.

### 6. Data requirements
- `users`: id, name, email, password_hash, role.
- `tasks`: id, title, description, completed, owner_id.
- SQLite is used for this learning exercise. The database file is stored in a persistent Docker volume during container deployment.

### 7. Non-functional requirements
- FastAPI provides interactive API documentation at `/docs`.
- The application listens on `0.0.0.0:8000` inside the container.
- The application can be built from a Dockerfile.
- A GitHub Actions workflow will later build and publish the Docker image and deploy it to EC2.
- Deployment should preserve the SQLite database using a persistent volume.
- A previous known-good image tag should be retained so the team can roll back by redeploying it.

### 8. Acceptance criteria
- A user can register and log in.
- A valid JWT allows access to protected routes.
- An invalid or missing JWT is rejected.
- Passwords in the database are hashes, not plain text.
- A user cannot read, update, or delete another user's tasks.
- An admin can access admin endpoints.
- Swagger UI is available at `/docs`.
- The Docker container runs the API on port 8000.
