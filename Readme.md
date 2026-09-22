# 🚀 Task Management API

A full-featured **Task Management System** built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **Docker**.

The project provides a complete backend for managing projects, tasks, members, roles, tags, subtasks, comments, dependencies, notifications, administration, logging, filtering, sorting, and pagination.

A simple frontend is also included for interacting with the API.

> **Note:** The frontend interface was generated with the assistance of AI.

---

## ✨ Features

- 🔐 JWT Authentication
- 👤 User registration and profile management
- 📁 Project management
- 👥 Project member management
- 🏷️ Project and task tags
- ✅ Task management
- 🔗 Task dependencies
- 📂 Subtasks
- 💬 Comments
- 🔔 Notifications
- 👑 Role-based access control
- 🛡️ Admin panel APIs
- 📊 Admin dashboard
- 📝 System activity logs
- 🔎 Filtering
- ↕️ Sorting
- 📄 Pagination
- 🗃️ Soft delete for projects and tasks
- 🐘 PostgreSQL database
- 🐳 Docker & Docker Compose
- 🔄 Database migrations with Alembic
- 🌐 Simple frontend

---

# 🛠️ Tech Stack

### Backend

- Python 3.14
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- Pydantic
- Uvicorn

### Frontend

- HTML
- CSS
- JavaScript
- Python HTTP Server

### DevOps

- Docker
- Docker Compose

---

# 🏗️ Architecture

The backend follows a layered architecture designed to keep business logic separated from HTTP and database concerns.

```text
Frontend
   │
   ▼
FastAPI Routers
   │
   ▼
Service Layer
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
```

The project also separates:

- Routers
- Services
- Schemas
- Database models
- Authentication & security
- Configuration
- Dependencies

---

# 📂 Main Components

The system is divided into several major domains:

```text
Authentication
Users
Projects
Project Members
Tasks
Task Dependencies
Tags
Subtasks
Comments
Notifications
Administration
Logs
Dashboard
```

---

# 🚀 Getting Started

## Prerequisites

You only need:

- Docker
- Docker Compose

No local Python or PostgreSQL installation is required.

---

# ▶️ Run the Project

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

Then start the application:

```bash
docker compose up -d
```

Docker Compose will build and start:

- PostgreSQL
- Backend
- Frontend

---

# 🗄️ Run Database Migrations

After the containers are created and the backend is running, enter the backend container:

```bash
docker exec -it backend bash
```

Then run:

```bash
alembic upgrade head
```

After the migration finishes, the database is ready.

You can exit the container with:

```bash
exit
```

> **That's all you need to do to run the project.**

---

# 🌐 Access the Application

### Frontend

```text
http://localhost
```

### Backend

```text
http://localhost:8000
```

### FastAPI Swagger Documentation

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

---

# 🔐 Authentication

The API uses **JWT Bearer Authentication**.

First obtain an access token:

```http
POST /token
```

Then send the token with authenticated requests:

```http
Authorization: Bearer <access_token>
```

The access token expires after **15 minutes**.

---

# 👥 Project Roles

Projects support four roles:

| Role      | Description                    |
| --------- | ------------------------------ |
| `owner`   | Full project control           |
| `manager` | Manage tasks, tags and members |
| `member`  | Access assigned tasks          |
| `viewer`  | Read-only access               |

Permissions are enforced by the backend based on the user's role within the project.

---

# 📡 API Overview

The API contains **71 endpoints** covering authentication, users, projects, tasks, administration, notifications, comments and more.

## Authentication

| Method | Endpoint | Description           |
| ------ | -------- | --------------------- |
| POST   | `/token` | Login and receive JWT |

---

## User

| Method | Endpoint         | Description                 |
| ------ | ---------------- | --------------------------- |
| POST   | `/user/`         | Register a new user         |
| GET    | `/user/`         | Get current user profile    |
| PUT    | `/user/`         | Update current user profile |
| PUT    | `/user/password` | Change password             |

---

## Projects

| Method | Endpoint                       | Description           |
| ------ | ------------------------------ | --------------------- |
| POST   | `/project/`                    | Create a project      |
| GET    | `/project/`                    | List user's projects  |
| GET    | `/project/{project_id}`        | Get project details   |
| PUT    | `/project/{project_id}`        | Update project        |
| DELETE | `/project/{project_id}`        | Soft delete project   |
| PATCH  | `/project/{project_id}/status` | Change project status |

---

## Project Members

| Method | Endpoint                                  | Description        |
| ------ | ----------------------------------------- | ------------------ |
| POST   | `/project/{project_id}/member`            | Add member         |
| GET    | `/project/{project_id}/members/`          | List members       |
| PATCH  | `/project/{project_id}/members/{user_id}` | Change member role |
| DELETE | `/project/{project_id}/members/{user_id}` | Remove member      |

---

## Tasks

All task endpoints use:

```text
/project/{project_id}/task
```

| Method | Endpoint            | Description        |
| ------ | ------------------- | ------------------ |
| POST   | `/`                 | Create task        |
| GET    | `/`                 | List tasks         |
| GET    | `/{task_id}`        | Get task details   |
| PUT    | `/{task_id}`        | Update task        |
| DELETE | `/{task_id}`        | Soft delete task   |
| PATCH  | `/status/{task_id}` | Change task status |

---

## Task Dependencies

| Method | Endpoint                                       | Description           |
| ------ | ---------------------------------------------- | --------------------- |
| GET    | `/project/{project_id}/task/depends/{task_id}` | Get task dependencies |
| DELETE | `/project/{project_id}/task/depends/{task_id}` | Delete dependencies   |

---

## Project Tags

| Method | Endpoint                                  | Description        |
| ------ | ----------------------------------------- | ------------------ |
| POST   | `/project/{project_id}/task/tag`          | Create project tag |
| GET    | `/project/{project_id}/task/tag`          | List project tags  |
| PUT    | `/project/{project_id}/task/tag/{tag_id}` | Update tag         |
| DELETE | `/project/{project_id}/task/tag/{tag_id}` | Delete tag         |

---

## Task Tags

| Method | Endpoint                                        | Description     |
| ------ | ----------------------------------------------- | --------------- |
| GET    | `/project/{project_id}/task/tag/task/{task_id}` | Get task tags   |
| POST   | `/project/{project_id}/task/tag/task/{task_id}` | Add tag to task |

---

## Subtasks

| Method | Endpoint                                                    | Description    |
| ------ | ----------------------------------------------------------- | -------------- |
| POST   | `/project/{project_id}/task/subtask/{task_id}`              | Create subtask |
| GET    | `/project/{project_id}/task/subtask/{task_id}`              | List subtasks  |
| PUT    | `/project/{project_id}/task/subtask/{task_id}/{subtask_id}` | Update subtask |
| DELETE | `/project/{project_id}/task/subtask/{task_id}/{subtask_id}` | Delete subtask |

---

## Comments

| Method | Endpoint                                                     | Description    |
| ------ | ------------------------------------------------------------ | -------------- |
| POST   | `/project/{project_id}/task/{task_id}/comments`              | Add comment    |
| GET    | `/project/{project_id}/task/{task_id}/comments`              | List comments  |
| PUT    | `/project/{project_id}/task/{task_id}/comments/{comment_id}` | Update comment |
| DELETE | `/project/{project_id}/task/{task_id}/comments/{comment_id}` | Delete comment |

### Mentions

Comments support user mentions using:

```text
@username
```

Mentioning a user automatically creates a notification.

---

# 🔔 Notifications

| Method | Endpoint                                                       | Description              |
| ------ | -------------------------------------------------------------- | ------------------------ |
| GET    | `/project/{project_id}/task/notification`                      | Get notifications        |
| GET    | `/project/{project_id}/task/notification/unread`               | Get unread notifications |
| GET    | `/project/{project_id}/task/notification/{id}`                 | Get notification         |
| GET    | `/project/{project_id}/task/notification/project`              | Project notifications    |
| GET    | `/project/{project_id}/task/notification/task/{task_id}`       | Task notifications       |
| GET    | `/project/{project_id}/task/notification/comment/{comment_id}` | Comment notifications    |
| PATCH  | `/project/{project_id}/task/notification/{id}/read`            | Mark as read             |
| PATCH  | `/project/{project_id}/task/notification/read-all`             | Mark all as read         |
| DELETE | `/project/{project_id}/task/notification/{id}`                 | Delete notification      |

> Currently, notifications are scoped under a project. A global user notification endpoint such as `/user/notifications` can be added in the future.

---

# 👑 Admin API

The project includes a dedicated administration API.

## Users

```text
GET     /admin/users
GET     /admin/users/{user_id}
PUT     /admin/users/{user_id}
PUT     /admin/users/password/{user_id}
DELETE  /admin/users/{user_id}
```

## Projects

```text
GET     /admin/projects
GET     /admin/projects/{project_id}
DELETE  /admin/projects/{project_id}
GET     /admin/projects/{project_id}/members
```

## Tasks

```text
GET     /admin/tasks
GET     /admin/tasks/{task_id}
DELETE  /admin/tasks/{task_id}
```

## Subtasks

```text
GET     /admin/subtask
GET     /admin/subtask/{task_id}
```

## Global Tags

```text
POST    /admin/tag
GET     /admin/tag
PUT     /admin/tag/{tag_id}
DELETE  /admin/tag/{tag_id}
GET     /admin/tag/project/{project_id}
```

## Logs

```text
GET /admin/logs
GET /admin/logs/user/{user_id}
GET /admin/logs/task/task/{task_id}
GET /admin/logs/project/{project_id}
GET /admin/logs/action/action/{action}
```

## Dashboard

```text
GET /admin/dashboard
```

---

# 🔎 Filtering, Sorting & Pagination

List endpoints support common query parameters.

### Pagination

```text
page
page_size
```

Default:

```text
page=1
page_size=20
```

Maximum page size:

```text
100
```

### Sorting

```text
sort_by
sort_order
```

Supported sort order:

```text
asc
desc
```

Example:

```http
GET /project/1/task?page=2&page_size=20&sort_by=created_at&sort_order=desc
```

Several list endpoints also provide domain-specific filters such as:

- User role
- Active status
- Tag scope
- Action
- Project/task related filters

---

# 🗃️ Soft Delete

Projects and tasks use **soft deletion**.

Instead of permanently removing the database record, the entity is marked as inactive and archived.

This approach helps preserve historical data and system logs.

---

# 🐘 Database

The application uses:

```text
PostgreSQL
```

Database migrations are managed with:

```text
Alembic
```

After starting the containers, migrations can be applied with:

```bash
docker exec -it backend bash
```

and:

```bash
alembic upgrade head
```

---

# 🐳 Docker Architecture

The application runs as three Docker services:

```text
                 ┌──────────────┐
                 │   Frontend   │
                 │   Port: 80   │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Backend    │
                 │  Port: 8000  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  PostgreSQL  │
                 │  Port: 5432  │
                 └──────────────┘
```

Docker Compose creates a dedicated network for communication between the services.

The PostgreSQL database uses a persistent Docker volume:

```text
postgres-data
```

so database data survives container recreation.

The backend waits for PostgreSQL to become healthy before starting through Docker Compose's health-check dependency configuration.

---

# 📦 Project Structure

A simplified structure of the project:

```text
TaskManagementApi/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── database/
│   │   └── core/
│   │
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── ...
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

# 🧪 API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, open:

```text
http://localhost:8000/docs
```

The Swagger interface allows you to:

- Explore endpoints
- Inspect request schemas
- Send API requests
- Authenticate using JWT
- Test responses directly from the browser

---

# 📌 Current Limitations

The current version does not include a file upload/attachment system.

Currently there are no endpoints for:

- User avatar upload
- Task attachments
- Project files

These can be added as future features.

---

# 🔮 Possible Future Improvements

Potential future extensions include:

- 📎 File attachments
- 🖼️ User avatars
- 📬 Global user notification endpoint
- ⚡ Redis caching
- 🔄 Celery background tasks
- 📧 Email notifications
- 🔔 Real-time notifications with WebSockets
- 🧪 Expanded automated test coverage
- 🔐 Refresh token system
- 🌐 Nginx reverse proxy
- 🚀 CI/CD with GitHub Actions
- 📈 Monitoring and metrics

---

# 👨‍💻 Development

To stop the application:

```bash
docker compose down
```

To rebuild the containers:

```bash
docker compose up -d --build
```

To view logs:

```bash
docker compose logs -f
```

To view backend logs only:

```bash
docker compose logs -f backend
```

---

# 📄 License

This project is intended as a personal backend development project and portfolio project.

---

# 🤖 AI Assistance

AI tools were used during the development process, including assistance with parts of the frontend implementation.

The backend architecture, API design, database models, business logic, authentication, authorization, Docker configuration, and project implementation were developed as part of the project's development process.
