# Employee Recommendation System

A backend system that recommends the most suitable employees for a project based on **skills, proficiency levels, experience, domain match, and availability**.

The system calculates a **weighted score** for each employee and returns the **top recommended candidates** for a given project.

---

# Project Overview

Organizations often struggle to assign the right employees to projects.  
This system helps automate that process by analyzing employee skillsets and project requirements to generate intelligent recommendations.

The recommendation score considers:

- Skill match
- Skill proficiency
- Experience
- Domain expertise
- Availability

---

# Tech Stack

- **FastAPI** – Backend API framework
- **PostgreSQL / Supabase** – Database
- **SQLAlchemy** – ORM for database interaction
- **Uvicorn** – ASGI server
- **Pydantic** – Data validation

---

# Features

- Employee CRUD operations
- Project CRUD operations
- Employee search by name
- Skill-based employee recommendation engine
- Weighted scoring algorithm
- REST API architecture

---

# Recommendation Algorithm

Employee score is calculated using weighted factors:

| Factor | Weight |
|------|------|
| Skill Match | 60% |
| Experience | 25% |
| Domain Match | 10% |
| Availability | 5% |

Final Score:
Final Score = Skill Score + Experience Score + Domain Score + Availability Score

Top employees are ranked based on the **highest final score**.

---
# Project Structure
project_root 
│ 
├── main.py 
│ 
├── database 
│ └── database.py │ 
├── models 
│ 
├── base.py │ 
├── employee.py 
│ 
├── project.py 
│ 
├── schemas 
│ ├── employee_schema.py 
│ ├── project_schema.py │ 
├── routes 
│ ├── employee_routes.py 
│ └── project_routes.py 
│ ├── services 
│ └── recommendation_service.py 
│ ├── .env 
└── README.md
---

# Installation Guide

## 1. Clone Repository

cd employee-recommendation-system

# 2. Create Virtual Environment

```bash
python -m venv venv
```
On Linux/Mac : source venv/bin/activate

On Windows : venv\Scripts\activate

# 3. Install Dependencies
```bash
pip install -r requirements.txt
```

# 4. Setup Database 
This project uses PostgreSQL (Supabase).

Create the required tables:

employee
project
skill
employee_skill
project_skill
```bash
postgresql://username:password@host:port/database
```
# 5. Run the Application
Start the FastAPI server:
```bash
uvicorn main:app --reload
```

# 6. API Documentation
Swagger UI
http://127.0.0.1:8000/docs
