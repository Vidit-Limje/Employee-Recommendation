from sqlalchemy import text
from fastapi import HTTPException
from models.project import Project


def recommend_employees_service(pid, db):

    project = db.query(Project).filter(Project.pid == pid).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    query = text("""
    
        -- Count number of required skills
        WITH skill_count AS (
            SELECT COUNT(*) AS total_skills
            FROM project_skill
            WHERE pid = :pid
        ),

        -- Calculate score for each skill
        skill_scores AS (
            SELECT
                e.eid,
                ps.skill_id,

                (60.0 / sc.total_skills) *
                CASE
                    WHEN es.proficiency_level >= ps.required_level THEN 1
                    WHEN es.proficiency_level >= ps.required_level * 0.66 THEN 0.75
                    WHEN es.proficiency_level >= ps.required_level * 0.33 THEN 0.50
                    ELSE 0.25
                END AS skill_score

            FROM employee e
            JOIN employee_skill es
                ON e.eid = es.eid
            JOIN project_skill ps
                ON es.skill_id = ps.skill_id
            CROSS JOIN skill_count sc
            WHERE ps.pid = :pid
        ),

        -- Sum skill score per employee
        employee_skill_total AS (
            SELECT
                eid,
                SUM(skill_score) AS total_skill_score
            FROM skill_scores
            GROUP BY eid
        )

        -- Final scoring
        SELECT
            e.eid,
            e.firstname,
            e.lastname,

            COALESCE(est.total_skill_score,0) AS skill_score,

            -- Experience score
            CASE
                WHEN p.required_experience = 0 THEN 25
                WHEN e.experience >= p.required_experience THEN 25
                ELSE (e.experience::float / p.required_experience) * 25
            END AS experience_score,

            -- Domain score
            CASE
                WHEN e.domain = p.domain THEN 10
                ELSE 0
            END AS domain_score,

            -- Availability score
            CASE
                WHEN e.availability = true THEN 5
                ELSE 0
            END AS availability_score,

            -- Final score
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

        FROM employee e
        LEFT JOIN employee_skill_total est
            ON e.eid = est.eid
        JOIN project p
            ON p.pid = :pid

        ORDER BY final_score DESC
        LIMIT 10
    """)

    result = db.execute(query, {"pid": pid})

    employees = [dict(row._mapping) for row in result]

    return {
        "project_id": pid,
        "recommendations": employees
    }