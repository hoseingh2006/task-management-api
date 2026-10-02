# 🚀 Task Management API

A full-featured **Task Management System** built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **Nginx**, and **Docker**.

The project provides a complete backend for managing projects, tasks, members, roles, tags, subtasks, comments, dependencies, notifications, administration, logging, filtering, sorting, and pagination.

A simple frontend is also included for interacting with the API, served through Nginx.

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
- 🌐 Nginx reverse proxy with HTTPS
- ⚖️ Load balancing across multiple backend instances
- 🚦 Rate limiting on API endpoints
- 🔄 Database migrations with Alembic
- 🖥️ Simple frontend

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
- Served via Nginx

### DevOps

- Docker
- Docker Compose
- Nginx (reverse proxy, HTTPS, load balancing, rate limiting)

---

# 🏗️ Architecture

The backend follows a layered architecture designed to keep business logic separated from HTTP and database concerns.

```text
Frontend (Nginx)
   │
   ▼
Nginx Reverse Proxy (HTTPS + Load Balancing)
   │
   ├──────────────┬──────────────┐
   ▼              ▼              ▼
Backend1       Backend2       Backend3
   │              │              │
   └──────────────┴──────────────┘
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

# 🔐 SSL Certificates

The Nginx container serves traffic over HTTPS and expects SSL certificates at:

```text
./certs/server.crt
./certs/server.key
```

Create a local `certs/` directory in the project root and place your certificate and key there.

For local development, you can generate a self-signed certificate:

```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/server.key \
  -out certs/server.crt \
  -subj "/CN=localhost"
```

The `certs/` directory is mounted read-only into the Nginx container via Docker Compose.

---

# ▶️ Run the Project

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

Make sure the SSL certificates exist (see the section above), then start the application:

```bash
docker compose up -d
```

Docker Compose will build and start:

- PostgreSQL
- Migration service (runs `alembic upgrade head` automatically)
- Backend 1
- Backend 2
- Backend 3
- Nginx (frontend + reverse proxy)

The migration service runs automatically before the backends start, so no manual migration step is required. However, you can still run migrations manually if needed (see below).

---

# 🗄️ Run Database Migrations Manually (Optional)

Migrations are applied automatically by the `migrate` service on startup. If you want to run them manually, enter one of the backend containers:

```bash
docker exec -it <backend_container_name> bash
```

Then run:

```bash
alembic upgrade head
```

You can exit the container with:

```bash
exit
```

---

# 🌐 Access the Application

### Frontend (HTTPS)

```text
https://localhost
```

> HTTP requests on port 80 are automatically redirected to HTTPS.

### Backend API (through Nginx)

```text
https://localhost/api/
```

### FastAPI Swagger Documentation

Because the API is proxied through Nginx under `/api/`, Swagger is available at:

```text
https://localhost/api/docs
```

### ReDoc

```text
https://localhost/api/redoc
```

> Direct backend access is not exposed to the host; all traffic goes through Nginx.

---

# 🛡️ Nginx Reverse Proxy

Nginx acts as the entry point for the whole application and provides:

- **HTTPS termination** with TLS 1.2 / TLS 1.3
- **HTTP → HTTPS redirect**
- **HTTP/2** support
- **Static file serving** for the frontend (`/usr/share/nginx/html`)
- **Reverse proxy** for the backend under the `/api/` path
- **Load balancing** across three backend instances (`backend1`, `backend2`, `backend3`)
- **Rate limiting** on API endpoints (`2r/s` per IP with a burst of 5)
- **Security headers**:
  - `Strict-Transport-Security`
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
- **Server token hiding** (`server_tokens off`)

The frontend uses the relative `API_BASE = '/api'`, so all API calls are automatically proxied through Nginx.

---

# 🔐 Authentication

The API uses **JWT Bearer Authentication**.

First obtain an access token:

```http
POST /api/token
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

> All endpoints below are accessed through Nginx with the `/api` prefix (e.g. `/api/token`, `/api/project/`, `/api/admin/users`).

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
GET /api/project/1/task?page=2&page_size=20&sort_by=created_at&sort_order=desc
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

Migrations run automatically on startup through the `migrate` Docker Compose service. Manual execution is also possible:

```bash
docker exec -it <backend_container_name> bash
```

and:

```bash
alembic upgrade head
```

The PostgreSQL database uses a persistent Docker volume (`postgres-data`) so data survives container recreation.

---

# 🐳 Docker Architecture

The application runs as multiple Docker services:

```text
                        ┌──────────────┐
                        │   Frontend   │
                        │   (Nginx)    │
                        │  443 / 80    │
                        └──────┬───────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │   Nginx Reverse    │
                    │   Proxy + LB       │
                    │   + Rate Limiting  │
                    └──────┬─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  ┌──────────┐       ┌──────────┐       ┌──────────┐
  │ Backend1 │       │ Backend2 │       │ Backend3 │
  │ Port 8000│       │ Port 8000│       │ Port 8000│
  └────┬─────┘       └────┬─────┘       └────┬─────┘
       └──────────────────┼──────────────────┘
                          ▼
                   ┌──────────────┐
                   │  PostgreSQL  │
                   │  Port 5432   │
                   └──────────────┘
```

Docker Compose creates a dedicated network (`Taskmanager`) for communication between the services.

A one-shot `migrate` service runs `alembic upgrade head` after PostgreSQL becomes healthy and before the backends start. Each backend waits for the migration service to complete successfully.

The Nginx container mounts the `./certs` directory read-only to serve HTTPS traffic.

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
│   └── ...
│
├── certs/
│   ├── server.crt
│   └── server.key
│
├── nginx.conf
├── Dockerfile          # Nginx image
├── compose.yaml
└── README.md
```

> The root `Dockerfile` builds the Nginx image: it copies `./frontend` into `/usr/share/nginx/html/` and `nginx.conf` into `/etc/nginx/nginx.conf`.

---

# 🧪 API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, open:

```text
https://localhost/api/docs
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
- 🚀 CI/CD with GitHub Actions
- 📈 Monitoring and metrics (Prometheus / Grafana)
- 🔑 Automatic Let's Encrypt certificate renewal

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
docker compose logs -f backend1
```

To view Nginx logs:

```bash
docker compose logs -f nginx
```

---

# 📄 License

This project is intended as a personal backend development project and portfolio project.

---

# 🤖 AI Assistance

AI tools were used during the development process, including assistance with parts of the frontend implementation.

The backend architecture, API design, database models, business logic, authentication, authorization, Docker configuration, Nginx configuration, and project implementation were developed as part of the project's development process.
