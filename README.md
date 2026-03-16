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

```
project_root
│
├── main.py
│
├── database
│   └── database.py
│
├── models
│   ├── base.py
│   ├── employee.py
│   └── project.py
│
├── schemas
│   ├── employee_schema.py
│   └── project_schema.py
│
├── routes
│   ├── employee_routes.py
│   └── project_routes.py
│
├── services
│   └── recommendation_service.py
│
├── .env
└── README.md
```

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

SQL Code-
```bash
-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.employee (
  eid integer NOT NULL DEFAULT nextval('employee_eid_seq'::regclass),
  firstname text NOT NULL,
  email text UNIQUE,
  phone text,
  domain text,
  experience integer,
  seniority text,
  availability boolean,
  lastname text,
  CONSTRAINT employee_pkey PRIMARY KEY (eid)
);
CREATE TABLE public.employee_skill (
  eid integer NOT NULL,
  skill_id integer NOT NULL,
  proficiency_level integer,
  CONSTRAINT employee_skill_pkey PRIMARY KEY (eid, skill_id),
  CONSTRAINT employee_skill_eid_fkey FOREIGN KEY (eid) REFERENCES public.employee(eid),
  CONSTRAINT employee_skill_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skill(skill_id)
);
CREATE TABLE public.project (
  pid integer NOT NULL DEFAULT nextval('project_pid_seq'::regclass),
  name text NOT NULL,
  client text,
  domain text,
  priority text,
  status text,
  required_experience integer DEFAULT 0,
  CONSTRAINT project_pkey PRIMARY KEY (pid)
);
CREATE TABLE public.project_allocation (
  eid integer NOT NULL,
  pid integer NOT NULL,
  assigned_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT project_allocation_pkey PRIMARY KEY (eid, pid),
  CONSTRAINT project_allocation_eid_fkey FOREIGN KEY (eid) REFERENCES public.employee(eid),
  CONSTRAINT project_allocation_pid_fkey FOREIGN KEY (pid) REFERENCES public.project(pid)
);
CREATE TABLE public.project_recommendation (
  eid integer NOT NULL,
  pid integer NOT NULL,
  score double precision,
  CONSTRAINT project_recommendation_pkey PRIMARY KEY (eid, pid),
  CONSTRAINT project_recommendation_eid_fkey FOREIGN KEY (eid) REFERENCES public.employee(eid),
  CONSTRAINT project_recommendation_pid_fkey FOREIGN KEY (pid) REFERENCES public.project(pid)
);
CREATE TABLE public.project_skill (
  pid integer NOT NULL,
  skill_id integer NOT NULL,
  required_level integer,
  CONSTRAINT project_skill_pkey PRIMARY KEY (pid, skill_id),
  CONSTRAINT project_skill_pid_fkey FOREIGN KEY (pid) REFERENCES public.project(pid),
  CONSTRAINT project_skill_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skill(skill_id)
);
CREATE TABLE public.skill (
  skill_id integer NOT NULL DEFAULT nextval('skill_skill_id_seq'::regclass),
  skill_name text UNIQUE,
  CONSTRAINT skill_pkey PRIMARY KEY (skill_id)
);
```
Database url-
Copy Paste Transaction Pooler URL for Example
```bash
postgresql://username:password@host:port/database
```
# 5. Run the Application
Start the FastAPI server:
```bash
uvicorn main:app --reload
```

# API Endpoints

## Employee APIs

| Method | Endpoint | Description |
|------|------|------|
| GET | `/employees/` | Get all employees |
| POST | `/employees/` | Add a new employee |
| GET | `/employees/search` | Search employee by name |
| GET | `/employees/{eid}` | Get employee by ID |
| PUT | `/employees/{eid}` | Update employee (full update) |
| PATCH | `/employees/{eid}` | Update employee (partial update) |
| DELETE | `/employees/{eid}` | Delete employee |

---

## Project APIs

| Method | Endpoint | Description |
|------|------|------|
| GET | `/projects/` | Get all projects |
| POST | `/projects/` | Create a new project |
| GET | `/projects/{pid}` | Get project by ID |
| PUT | `/projects/{pid}` | Update project |
| DELETE | `/projects/{pid}` | Delete project |
| GET | `/projects/{pid}/recommendations` | Get recommended employees for a project |

---

## API Base URL

When running locally:

```bash
http://127.0.0.1:8000
```

### Example request:
```bash
GET http://127.0.0.1:8000/projects/1/recommendations
```


---

## Interactive API Docs

FastAPI automatically provides interactive documentation.

| Tool | URL |
|-----|-----|
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |

# 6. API Documentation
Swagger UI
http://127.0.0.1:8000/docs
