import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .dependencies import get_current_user, require_admin
from .models import Task, User
from .schemas import (
    LoginRequest,
    RegisterRequest,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
    TokenResponse,
    UserResponse,
)
from .security import create_access_token, hash_password, verify_password


def create_admin_if_configured():
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    name = os.getenv("ADMIN_NAME", "Project Admin")
    if not email or not password:
        return

    from .database import SessionLocal
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == email.lower()))
        if existing is None:
            admin = User(
                name=name,
                email=email.lower(),
                password_hash=hash_password(password),
                role="admin",
            )
            db.add(admin)
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    create_admin_if_configured()
    yield


app = FastAPI(
    title="Task Manager API",
    description="Practice project for FastAPI, JWT, Docker, and CI/CD.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def home():
    return {"message": "Task Manager API is running", "docs": "/docs"}


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")

    user = User(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role="user",  # Public registration can never assign admin privileges.
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return TokenResponse(access_token=create_access_token(user.id, user.role))


@app.get("/auth/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(
        title=data.title,
        description=data.description,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list(db.scalars(select(Task).where(Task.owner_id == current_user.id)).all())


def get_task_or_404(task_id: int, db: Session, current_user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You cannot access this task")
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_task_or_404(task_id, db, current_user)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db, current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_or_404(task_id, db, current_user)
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@app.get("/admin/users", response_model=list[UserResponse])
def admin_list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return list(db.scalars(select(User).order_by(User.id)).all())


@app.get("/admin/tasks", response_model=list[TaskResponse])
def admin_list_all_tasks(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return list(db.scalars(select(Task).order_by(Task.id)).all())
