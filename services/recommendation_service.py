# -----------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------

# text → allows execution of raw SQL queries using SQLAlchemy
from sqlalchemy import text

# HTTPException → used to return HTTP error responses from FastAPI
from fastapi import HTTPException

# Project → SQLAlchemy ORM model representing project table
from models.project import Project


# -----------------------------------------------------------
# EMPLOYEE RECOMMENDATION SERVICE
# -----------------------------------------------------------

def recommend_employees_service(pid, db):
    """
    This service recommends the best employees for a given project.

    The recommendation score is calculated using:

    1️⃣ Skill Match Score        → 60 points
    2️⃣ Experience Score         → 25 points
    3️⃣ Domain Match Score       → 10 points
    4️⃣ Availability Score       → 5 points

    Total Maximum Score = 100 points

    This function returns the top 10 employees sorted by highest score.
    """

    # -------------------------------------------------
    # STEP 1: CHECK IF PROJECT EXISTS
    # -------------------------------------------------

    # Query the project table to check if the given project ID exists
    project = db.query(Project).filter(Project.pid == pid).first()

    # If project does not exist → return HTTP 404 error
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")


    # -------------------------------------------------
    # STEP 2: DEFINE SQL QUERY FOR RECOMMENDATION
    # -------------------------------------------------

    # Using raw SQL because recommendation queries can be complex
    # and SQL performs better for aggregation and scoring

    query = text("""

        ------------------------------------------------------
        -- STEP A: COUNT TOTAL REQUIRED SKILLS FOR PROJECT
        ------------------------------------------------------

        WITH skill_count AS (
            SELECT COUNT(*) AS total_skills
            FROM project_skill
            WHERE pid = :pid
        ),


        ------------------------------------------------------
        -- STEP B: CALCULATE SKILL SCORE FOR EACH EMPLOYEE
        ------------------------------------------------------

        skill_scores AS (
            SELECT
                e.eid,
                ps.skill_id,

                -- Skill weight = 60 points divided among required skills
                (60.0 / NULLIF(sc.total_skills,0)) *

                CASE
                    -- Full score if employee proficiency >= required level
                    WHEN es.proficiency_level >= ps.required_level THEN 1

                    -- 75% score if proficiency >= 66% of required
                    WHEN es.proficiency_level >= ps.required_level * 0.66 THEN 0.75

                    -- 50% score if proficiency >= 33% of required
                    WHEN es.proficiency_level >= ps.required_level * 0.33 THEN 0.50

                    -- Minimum score otherwise
                    ELSE 0.25
                END AS skill_score

            FROM employee e

            -- Join employee skills
            JOIN employee_skill es
                ON e.eid = es.eid

            -- Join project required skills
            JOIN project_skill ps
                ON es.skill_id = ps.skill_id

            -- Cross join to get total skill count
            CROSS JOIN skill_count sc

            WHERE ps.pid = :pid
        ),


        ------------------------------------------------------
        -- STEP C: SUM SKILL SCORES PER EMPLOYEE
        ------------------------------------------------------

        employee_skill_total AS (
            SELECT
                eid,
                SUM(skill_score) AS total_skill_score
            FROM skill_scores
            GROUP BY eid
        )


        ------------------------------------------------------
        -- STEP D: FINAL SCORING CALCULATION
        ------------------------------------------------------

        SELECT
            e.eid,
            e.firstname,
            e.lastname,

            -- Skill score (max 60)
            COALESCE(est.total_skill_score,0) AS skill_score,


            --------------------------------------------------
            -- EXPERIENCE DATA
            --------------------------------------------------

            e.experience AS employee_experience,
            p.required_experience,


            --------------------------------------------------
            -- DOMAIN DATA
            --------------------------------------------------

            e.domain AS employee_domain,
            p.domain AS project_domain,


            --------------------------------------------------
            -- AVAILABILITY DATA
            --------------------------------------------------

            e.availability,


            --------------------------------------------------
            -- EXPERIENCE SCORE (max 25)
            --------------------------------------------------

            CASE
                -- If project requires no experience
                WHEN p.required_experience = 0 THEN 25

                -- If employee meets requirement
                WHEN e.experience >= p.required_experience THEN 25

                -- Otherwise give proportional score
                ELSE (e.experience::float / p.required_experience) * 25
            END AS experience_score,


            --------------------------------------------------
            -- DOMAIN MATCH SCORE (max 10)
            --------------------------------------------------

            CASE
                WHEN e.domain = p.domain THEN 10
                ELSE 0
            END AS domain_score,


            --------------------------------------------------
            -- AVAILABILITY SCORE (max 5)
            --------------------------------------------------

            CASE
                WHEN e.availability = true THEN 5
                ELSE 0
            END AS availability_score,


            --------------------------------------------------
            -- FINAL SCORE CALCULATION
            --------------------------------------------------

            (
                COALESCE(est.total_skill_score,0)

                +
                CASE
                    WHEN p.required_experience = 0 THEN 25
                    WHEN e.experience >= p.required_experience THEN 25
                    ELSE (e.experience::float / p.required_experience) * 25
                END

                +
                CASE
                    WHEN e.domain = p.domain THEN 10
                    ELSE 0
                END

                +
                CASE
                    WHEN e.availability = true THEN 5
                    ELSE 0
                END

            ) AS final_score


        ------------------------------------------------------
        -- JOIN TABLES
        ------------------------------------------------------

        FROM employee e

        LEFT JOIN employee_skill_total est
            ON e.eid = est.eid

        JOIN project p
            ON p.pid = :pid


        ------------------------------------------------------
        -- SORT BY BEST EMPLOYEE
        ------------------------------------------------------

        ORDER BY final_score DESC

        LIMIT 10

    """)


    # -------------------------------------------------
    # STEP 3: EXECUTE SQL QUERY
    # -------------------------------------------------

    # :pid parameter is replaced safely (prevents SQL injection)
    result = db.execute(query, {"pid": pid})


    # This list will store final employee recommendations
    employees = []


    # -------------------------------------------------
    # STEP 4: BUILD HUMAN-READABLE EXPLANATION
    # -------------------------------------------------

    for row in result:

        # Convert SQL row to dictionary
        data = dict(row._mapping)

        explanation = {}

        # -------------------------------------------------
        # SKILL EXPLANATION
        # -------------------------------------------------

        explanation["skills"] = (
            f"Skill match contributed {round(data['skill_score'],2)} points"
        )


        # -------------------------------------------------
        # EXPERIENCE EXPLANATION
        # -------------------------------------------------

        if data["employee_experience"] >= data["required_experience"]:

            explanation["experience"] = (
                f"Employee has {data['employee_experience']} years experience "
                f"which meets the project requirement "
                f"({data['required_experience']} years)"
            )

        else:

            explanation["experience"] = (
                f"Employee has {data['employee_experience']} years experience "
                f"but project requires {data['required_experience']} years"
            )


        # -------------------------------------------------
        # DOMAIN EXPLANATION
        # -------------------------------------------------

        if data["employee_domain"] == data["project_domain"]:

            explanation["domain"] = "Employee domain matches project domain"

        else:

            explanation["domain"] = "Employee domain does not match project domain"


        # -------------------------------------------------
        # AVAILABILITY EXPLANATION
        # -------------------------------------------------

        if data["availability"]:

            explanation["availability"] = "Employee is available for assignment"

        else:

            explanation["availability"] = "Employee is currently unavailable"


        # -------------------------------------------------
        # BUILD EMPLOYEE OBJECT
        # -------------------------------------------------

        employees.append({

            "eid": data["eid"],
            "firstname": data["firstname"],
            "lastname": data["lastname"],

            # Detailed scoring breakdown
            "scores": {
                "skills": data["skill_score"],
                "experience": data["experience_score"],
                "domain": data["domain_score"],
                "availability": data["availability_score"]
            },

            # Final total score
            "final_score": data["final_score"],

            # Human-readable explanation
            "explanation": explanation
        })


    # -------------------------------------------------
    # STEP 5: FINAL API RESPONSE
    # -------------------------------------------------

    return {

        # Project for which recommendation was generated
        "project_id": pid,

        # Top recommended employees
        "recommendations": employees
    }