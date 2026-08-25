from fastapi import FastAPI
from .routers import auth, route_admin, route_project, route_task, route_user

app = FastAPI()
app.include_router(route_admin.route, prefix="/admin", tags=["ADMIN"])
app.include_router(route_project.route, prefix="/project", tags=["PROJECT"])
app.include_router(route_task.route, prefix="/project/{project_id}/task", tags=["TASK"])
app.include_router(route_user.route, prefix="/user", tags=["USER"])
app.include_router(auth.route, tags=["AUTH"])
