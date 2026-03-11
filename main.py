# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================
# This file is the starting point of the FastAPI application.
# When the server starts (using uvicorn), this file is loaded
# and the FastAPI app instance is created.
#
# Example run command:
# uvicorn main:app --reload
#
# main -> filename
# app  -> FastAPI object inside this file
# =====================================================


# Import FastAPI framework
# FastAPI is used to build REST APIs quickly with automatic
# validation, documentation, and async support.
from fastapi import FastAPI


# -----------------------------------------------------
# Import route modules
# -----------------------------------------------------
# Instead of defining all API endpoints inside main.py,
# we organize them into separate route files for better
# scalability and maintainability.
#
# employee_routes.py -> contains employee CRUD APIs
# project_routes.py  -> contains project APIs and recommendation APIs
#
# Each route file defines an APIRouter object named "router".
# We import them and register them with the FastAPI app.

from routes.employee_routes import router as employee_router
from routes.project_routes import router as project_router


# -----------------------------------------------------
# Create FastAPI Application Instance
# -----------------------------------------------------
# This creates the main FastAPI application object.
# All API routes, middleware, and configurations are attached
# to this object.
#
# Parameters:
#
# title       -> Name of the API shown in Swagger UI
# description -> Explanation of what this API does
# version     -> Version of the API (useful for versioning)
#
# Once this object is created, it becomes the central controller
# for handling all incoming HTTP requests.

app = FastAPI(
    title="Employee Recommendation System",
    description="API to manage employees and recommend them for projects",
    version="1.0"
)


# -----------------------------------------------------
# Register Employee Routes
# -----------------------------------------------------
# include_router() attaches all endpoints defined in
# employee_routes.py to the main FastAPI application.
#
# Since employee_routes.py defines:
#
# router = APIRouter(prefix="/employees")
#
# All employee endpoints will automatically start with:
#
# /employees
#
# Examples:
#
# POST  /employees
# GET   /employees
# GET   /employees/{eid}
# PUT   /employees/{eid}
# PATCH /employees/{eid}
# DELETE /employees/{eid}

app.include_router(employee_router)


# -----------------------------------------------------
# Register Project Routes
# -----------------------------------------------------
# This registers all project-related APIs with the application.
#
# Since project_routes.py defines:
#
# router = APIRouter(prefix="/projects")
#
# The following endpoints will exist:
#
# POST   /projects
# GET    /projects
# GET    /projects/{pid}
# PUT    /projects/{pid}
# DELETE /projects/{pid}
#
# Recommendation API:
#
# GET /projects/{pid}/recommendations
#
# This endpoint uses a scoring algorithm to recommend
# employees based on:
#
# 1. Skill match
# 2. Experience
# 3. Domain match
# 4. Availability

app.include_router(project_router)


# =====================================================
# FINAL RESULTING API ENDPOINT STRUCTURE
# =====================================================
#
# EMPLOYEE APIs
#
# POST   /employees
# GET    /employees
# GET    /employees/search
# GET    /employees/{eid}
# PUT    /employees/{eid}
# PATCH  /employees/{eid}
# DELETE /employees/{eid}
#
#
# PROJECT APIs
#
# POST   /projects
# GET    /projects
# GET    /projects/{pid}
# PUT    /projects/{pid}
# DELETE /projects/{pid}
#
#
# RECOMMENDATION API
#
# GET /projects/{pid}/recommendations
#
# This API calculates employee ranking using weighted scoring.
#
# =====================================================


# =====================================================
# AUTOMATIC API DOCUMENTATION
# =====================================================
#
# FastAPI automatically generates documentation.
#
# Swagger UI:
# http://127.0.0.1:8000/docs
#
# ReDoc:
# http://127.0.0.1:8000/redoc
#
# These interfaces allow testing the APIs directly
# without using Postman.
#
# =====================================================