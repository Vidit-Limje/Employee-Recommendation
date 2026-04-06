# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================

from fastapi import FastAPI


# -----------------------------------------------------
# IMPORT ROUTERS
# -----------------------------------------------------

from routes.employee_routes import router as employee_router
from routes.project_routes import router as project_router
from routes.skill_routes import router as skill_router
from routes.auth_routes import router as auth_router   # ✅ NEW


# -----------------------------------------------------
# CREATE FASTAPI APP
# -----------------------------------------------------

app = FastAPI(
    title="Employee Recommendation System",
    description="API to manage employees, skills, and recommend them for projects with JWT Authentication",
    version="2.0"   # ✅ bumped version
)


# -----------------------------------------------------
# REGISTER ROUTES
# -----------------------------------------------------

# 🔐 Auth Routes (IMPORTANT: keep first for clarity)
app.include_router(auth_router)

# 👨‍💼 Employee Routes
app.include_router(employee_router)

# 📁 Project Routes
app.include_router(project_router)

# 🧠 Skill Routes
app.include_router(skill_router)


# =====================================================
# ROOT ENDPOINT (OPTIONAL BUT USEFUL)
# =====================================================

@app.get("/")
def root():
    return {
        "message": "Employee Recommendation API with JWT Auth is running 🚀",
        "docs": "/docs"
    }


# =====================================================
# FINAL API ENDPOINT STRUCTURE
# =====================================================

"""
🔐 AUTH APIs (NEW)

POST   /auth/signup
POST   /auth/login


👨‍💼 EMPLOYEE APIs

POST   /employees
GET    /employees
GET    /employees/search
GET    /employees/{eid}
PUT    /employees/{eid}
PATCH  /employees/{eid}
DELETE /employees/{eid}


🧠 EMPLOYEE SKILL APIs

POST   /employees/{eid}/skills
GET    /employees/{eid}/skills
GET    /employees/{eid}/skills/details
DELETE /employees/{eid}/skills/{skill_id}


📁 PROJECT APIs

POST   /projects
GET    /projects
GET    /projects/{pid}
PUT    /projects/{pid}
DELETE /projects/{pid}


🧠 SKILL APIs

POST   /skills
GET    /skills
DELETE /skills/{skill_id}


🤖 RECOMMENDATION API

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