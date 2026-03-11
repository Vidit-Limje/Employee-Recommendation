from fastapi import FastAPI

# Import route modules
from routes.employee_routes import router as employee_router
from routes.project_routes import router as project_router

# Create FastAPI app
app = FastAPI(
    title="Employee Recommendation System",
    description="API to manage employees and recommend them for projects",
    version="1.0"
)

# Register routes
app.include_router(employee_router)
app.include_router(project_router)