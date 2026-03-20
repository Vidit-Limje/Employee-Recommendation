# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================

from fastapi import FastAPI


# -----------------------------------------------------
# IMPORT ROUTERS
# -----------------------------------------------------

from routes.employee_routes import router as employee_router
from routes.project_routes import router as project_router
from routes.skill_routes import router as skill_router   # ✅ NEW


# -----------------------------------------------------
# CREATE FASTAPI APP
# -----------------------------------------------------

app = FastAPI(
    title="Employee Recommendation System",
    description="API to manage employees, skills, and recommend them for projects",
    version="1.1"   # ✅ bumped version
)


# -----------------------------------------------------
# REGISTER ROUTES
# -----------------------------------------------------

# Employee Routes
app.include_router(employee_router)

# Project Routes
app.include_router(project_router)

# Skill Routes (NEW)
app.include_router(skill_router)


# =====================================================
# FINAL API ENDPOINT STRUCTURE
# =====================================================

"""
EMPLOYEE APIs

POST   /employees
GET    /employees
GET    /employees/search
GET    /employees/{eid}
PUT    /employees/{eid}
PATCH  /employees/{eid}
DELETE /employees/{eid}


EMPLOYEE SKILL APIs (NEW)

POST   /employees/{eid}/skills
GET    /employees/{eid}/skills
GET    /employees/{eid}/skills/details
DELETE /employees/{eid}/skills/{skill_id}


PROJECT APIs

POST   /projects
GET    /projects
GET    /projects/{pid}
PUT    /projects/{pid}
DELETE /projects/{pid}


SKILL APIs (NEW)

POST   /skills
GET    /skills
DELETE /skills/{skill_id}


RECOMMENDATION API

GET /projects/{pid}/recommendations
"""


# =====================================================
# API DOCUMENTATION
# =====================================================

"""
Swagger UI:
http://127.0.0.1:8000/docs

ReDoc:
http://127.0.0.1:8000/redoc
"""