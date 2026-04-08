from sqlalchemy import text
from fastapi import HTTPException
from models.project import Project


def recommend_employees_service(pid, db):

    # ✅ Check project exists
    project = db.query(Project).filter(Project.pid == pid).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # ✅ UPDATED SQL QUERY (NULL SAFE)
    query = text("""
        WITH skill_count AS (
            SELECT COUNT(*) AS total_skills
            FROM project_skill
            WHERE pid = :pid
        ),

        skill_scores AS (
            SELECT
                e.eid,
                (60.0 / NULLIF(sc.total_skills,0)) *
                CASE
                    WHEN es.proficiency_level >= ps.required_level THEN 1
                    WHEN es.proficiency_level >= ps.required_level * 0.66 THEN 0.75
                    WHEN es.proficiency_level >= ps.required_level * 0.33 THEN 0.50
                    ELSE 0.25
                END AS skill_score
            FROM employee e
            JOIN employee_skill es ON e.eid = es.eid
            JOIN project_skill ps ON es.skill_id = ps.skill_id
            CROSS JOIN skill_count sc
            WHERE ps.pid = :pid
        ),

        employee_skill_total AS (
            SELECT eid, SUM(skill_score) AS total_skill_score
            FROM skill_scores
            GROUP BY eid
        )

        SELECT
            e.eid,
            e.firstname,
            e.lastname,

            COALESCE(est.total_skill_score,0) AS skill_score,

            -- ✅ FIXED NULL HANDLING
            COALESCE(e.experience,0) AS employee_experience,
            COALESCE(p.required_experience,0) AS required_experience,

            e.domain AS employee_domain,
            p.domain AS project_domain,

            COALESCE(e.availability,false) AS availability,

            -- ✅ SAFE EXPERIENCE SCORE
            CASE
                WHEN COALESCE(p.required_experience,0) = 0 THEN 25
                WHEN COALESCE(e.experience,0) >= COALESCE(p.required_experience,0) THEN 25
                ELSE (COALESCE(e.experience,0)::float / NULLIF(p.required_experience,0)) * 25
            END AS experience_score,

            CASE
                WHEN e.domain = p.domain THEN 10
                ELSE 0
            END AS domain_score,

            CASE
                WHEN e.availability = true THEN 5
                ELSE 0
            END AS availability_score,

            (
                COALESCE(est.total_skill_score,0)
                +
                CASE
                    WHEN COALESCE(p.required_experience,0) = 0 THEN 25
                    WHEN COALESCE(e.experience,0) >= COALESCE(p.required_experience,0) THEN 25
                    ELSE (COALESCE(e.experience,0)::float / NULLIF(p.required_experience,0)) * 25
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

        FROM employee e
        LEFT JOIN employee_skill_total est ON e.eid = est.eid
        JOIN project p ON p.pid = :pid

        ORDER BY final_score DESC
        LIMIT 10
    """)

    result = db.execute(query, {"pid": pid})

    employees = []

    for row in result:
        data = dict(row._mapping)

        # ✅ DOUBLE SAFETY (Python side)
        emp_exp = data.get("employee_experience", 0) or 0
        req_exp = data.get("required_experience", 0) or 0

        explanation = {}

        explanation["skills"] = f"Skill match contributed {round(data['skill_score'],2)} points"

        if emp_exp >= req_exp:
            explanation["experience"] = f"Employee has {emp_exp} years experience (meets requirement)"
        else:
            explanation["experience"] = f"Employee has {emp_exp} years but needs {req_exp}"

        explanation["domain"] = (
            "Domain match" if data["employee_domain"] == data["project_domain"]
            else "Domain mismatch"
        )

        explanation["availability"] = (
            "Available" if data["availability"]
            else "Not available"
        )

        employees.append({
            "eid": data["eid"],
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "scores": {
                "skills": data["skill_score"],
                "experience": data["experience_score"],
                "domain": data["domain_score"],
                "availability": data["availability_score"]
            },
            "final_score": data["final_score"],
            "explanation": explanation
        })

    return {
        "project_id": pid,
        "recommendations": employees
    }