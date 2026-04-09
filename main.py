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
from routes.auth_routes import router as auth_router

# -----------------------------------------------------
# REDIS + DB + CACHE IMPORTS
# -----------------------------------------------------

from utils.redis_client import redis_client
from database.database import SessionLocal
from utils.permissions import get_permissions_for_role

# -----------------------------------------------------
# CREATE FASTAPI APP
# -----------------------------------------------------

app = FastAPI(
    title="Employee Recommendation System",
    description="API to manage employees, skills, and recommend them for projects with JWT Authentication + Redis Caching",
    version="3.0"   # 🚀 bumped version
)

# -----------------------------------------------------
# STARTUP EVENTS (CACHE WARMING + HEALTH CHECK)
# -----------------------------------------------------

@app.on_event("startup")
def startup_event():
    print("🚀 Starting application...")

    # ✅ Check Redis connection
    try:
        redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print("❌ Redis connection failed:", e)

    # ✅ Warm RBAC cache (preload permissions)
    try:
        db = SessionLocal()

        roles = ["admin", "employee"]  # adjust if needed

        for role in roles:
            get_permissions_for_role(role, db)

        db.close()
        print("🔥 RBAC cache warmed successfully")

    except Exception as e:
        print("❌ Cache warming failed:", e)


# -----------------------------------------------------
# REGISTER ROUTES
# -----------------------------------------------------

# 🔐 Auth Routes
app.include_router(auth_router)

# 👨‍💼 Employee Routes
app.include_router(employee_router)

# 📁 Project Routes
app.include_router(project_router)

# 🧠 Skill Routes
app.include_router(skill_router)


# =====================================================
# ROOT ENDPOINT
# =====================================================

@app.get("/")
def root():
    return {
        "message": "Employee Recommendation API with JWT + Redis is running 🚀",
        "docs": "/docs",
        "health": "/health"
    }


# =====================================================
# HEALTH CHECK ENDPOINTS (PRODUCTION STANDARD)
# =====================================================

@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "services": {
            "api": "running"
        }
    }


@app.get("/health/redis")
def redis_health():
    try:
        redis_client.ping()
        return {
            "status": "OK",
            "redis": "connected"
        }
    except Exception:
        return {
            "status": "ERROR",
            "redis": "not connected"
        }


# =====================================================
# FINAL API ENDPOINT STRUCTURE
# =====================================================

"""
🔐 AUTH APIs

POST   /auth/signup
POST   /auth/login


👨‍💼 EMPLOYEE APIs

GET    /employees
GET    /employees/me
PATCH  /employees/me
GET    /employees/id/{eid}
PATCH  /employees/id/{eid}
DELETE /employees/id/{eid}


🧠 SKILL APIs

POST   /skills
GET    /skills
DELETE /skills/{skill_id}


📁 PROJECT APIs

POST   /projects
GET    /projects
GET    /projects/{pid}
PUT    /projects/{pid}
DELETE /projects/{pid}


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