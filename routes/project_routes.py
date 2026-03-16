# -----------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------

# APIRouter → Used to group related API routes
# Depends → Used for dependency injection (ex: database session)
# HTTPException → Used to return HTTP error responses
from fastapi import APIRouter, Depends, HTTPException

# Session → SQLAlchemy database session used to interact with database
from sqlalchemy.orm import Session


# get_db → Function that provides database session
# Usually implemented with a generator that opens a DB connection
# and automatically closes it after the request finishes
from database.database import get_db


# Project → SQLAlchemy ORM model representing the "projects" table
# Each instance corresponds to one row in the database
from models.project import Project


# Import Pydantic schemas used for request validation and response formatting
from schemas.project_schema import (

    # Used when creating a new project
    # Defines required fields expected in request body
    ProjectCreate,

    # Used when performing full update (PUT)
    ProjectUpdate,

    # Used when performing partial update (PATCH)
    ProjectPartialUpdate,

    # Used as response schema
    # Controls what data is returned to the client
    ProjectResponse
)


# Import recommendation service
# This service contains business logic for recommending employees
# based on project requirements
from services.recommendation_service import recommend_employees_service


# -----------------------------------------------------------
# ROUTER CONFIGURATION
# -----------------------------------------------------------

# APIRouter groups endpoints related to projects
# prefix="/projects" → all endpoints start with /projects
# tags=["Projects"] → used in Swagger documentation grouping
router = APIRouter(prefix="/projects", tags=["Projects"])



# -----------------------------------------------------------
# CREATE PROJECT
# -----------------------------------------------------------

@router.post(
    "/",                     # endpoint path → /projects/
    status_code=201,         # HTTP status returned on success
    response_model=ProjectResponse  # Response must follow this schema
)
def create_project(
    project: ProjectCreate,           # Request body schema
    db: Session = Depends(get_db)     # Inject database session
):
    """
    Create a new project in the database.

    Endpoint:
    POST /projects/

    Request Body Example:
    {
        "name": "AI Recommendation System",
        "domain": "Machine Learning",
        "required_skills": "Python, ML, SQL",
        "team_size": 4,
        "deadline": "2026-05-01"
    }

    Response Example:
    {
        "id": 1,
        "name": "AI Recommendation System",
        "domain": "Machine Learning",
        "required_skills": "Python, ML, SQL",
        "team_size": 4,
        "deadline": "2026-05-01"
    }
    """

    # Convert validated Pydantic object to dictionary
    # model_dump() returns dictionary of fields
    new_project = Project(**project.model_dump())

    # Add new object to database session
    db.add(new_project)

    # Commit transaction → writes changes to database
    db.commit()

    # Refresh object to load auto-generated values (like id)
    db.refresh(new_project)

    # Return created project
    return new_project



# -----------------------------------------------------------
# GET ALL PROJECTS
# -----------------------------------------------------------

@router.get(
    "/", 
    response_model=list[ProjectResponse]
)
def get_projects(db: Session = Depends(get_db)):
    """
    Fetch all projects from database.

    Endpoint:
    GET /projects/

    Response Example:
    [
        {
            "id": 1,
            "name": "AI Recommendation System"
        },
        {
            "id": 2,
            "name": "Cloud Migration"
        }
    ]
    """

    # Query all rows from Project table
    projects = db.query(Project).all()

    # Return list of projects
    return projects



# -----------------------------------------------------------
# GET PROJECT BY ID
# -----------------------------------------------------------

@router.get(
    "/{pid}",
    response_model=ProjectResponse
)
def get_project(pid: int, db: Session = Depends(get_db)):
    """
    Fetch a specific project using its ID.

    Endpoint:
    GET /projects/{pid}

    Example:
    /projects/5

    Response Example:
    {
        "id": 5,
        "name": "Cloud Migration",
        "domain": "DevOps"
    }

    Error Response:
    {
        "detail": "Project not found"
    }
    """

    # db.get() retrieves record by primary key
    project = db.get(Project, pid)

    # If project does not exist → return HTTP 404 error
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project



# -----------------------------------------------------------
# UPDATE PROJECT (FULL UPDATE)
# -----------------------------------------------------------

@router.put(
    "/{pid}",
    response_model=ProjectResponse
)
def update_project(
    pid: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Fully update an existing project.

    HTTP Method:
    PUT → replaces the entire resource

    Endpoint:
    PUT /projects/{pid}

    Request Body Example:
    {
        "name": "Updated Project",
        "domain": "AI",
        "required_skills": "Python, TensorFlow"
    }

    Response Example:
    {
        "id": 3,
        "name": "Updated Project",
        "domain": "AI",
        "required_skills": "Python, TensorFlow"
    }
    """

    # Retrieve project from database
    proj = db.get(Project, pid)

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Convert Pydantic object into dictionary
    for key, value in project.model_dump().items():

        # setattr dynamically updates object attributes
        # Example:
        # setattr(proj, "name", "New Project Name")
        setattr(proj, key, value)

    # Commit changes to database
    db.commit()

    # Refresh object to reflect updated values
    db.refresh(proj)

    return proj



# -----------------------------------------------------------
# DELETE PROJECT
# -----------------------------------------------------------

@router.delete("/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):
    """
    Delete a project from the database.

    Endpoint:
    DELETE /projects/{pid}

    Example:
    DELETE /projects/4

    Success Response:
    {
        "message": "Project 4 deleted successfully"
    }

    Error Response:
    {
        "detail": "Project not found"
    }
    """

    # Retrieve project
    proj = db.get(Project, pid)

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete record
    db.delete(proj)

    # Commit deletion
    db.commit()

    return {"message": f"Project {pid} deleted successfully"}



# -----------------------------------------------------------
# EMPLOYEE RECOMMENDATION FOR PROJECT
# -----------------------------------------------------------

@router.get("/{pid}/recommendations")
def recommend_employees(pid: int, db: Session = Depends(get_db)):
    """
    Recommend best employees for a specific project.

    Endpoint:
    GET /projects/{pid}/recommendations

    Example:
    /projects/3/recommendations

    This endpoint calls a separate service layer function:
    recommend_employees_service()

    The service usually performs:
    - Skill matching
    - Experience matching
    - Domain compatibility
    - Availability filtering
    - Weighted scoring

    Example Response:
    [
        {
            "employee_id": 12,
            "name": "John Doe",
            "match_score": 0.87
        },
        {
            "employee_id": 8,
            "name": "Alice Smith",
            "match_score": 0.82
        }
    ]
    """

    # Call recommendation service
    # Service handles business logic and scoring
    return recommend_employees_service(pid, db)