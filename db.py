import psycopg2
from sentence_transformers import SentenceTransformer

DB_CONFIG = {
    "dbname": "resumes_db",
    "user": "postgres",
    "password": "mysecretpassword",
    "host": "localhost",
    "port": 5433
}

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_resume_embedding(text):
    return model.encode(text).tolist()

def insert_resume_into_db(conn, structured_info, cleaned_text):
    embedding = get_resume_embedding(cleaned_text)

    with conn.cursor() as cur:
        skills_array = structured_info.get("skills") or []

        cur.execute("""
            INSERT INTO resumes (
                name, location, current_job_title, preferred_job_title, 
                skills, inline_resume, embedding
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            structured_info.get("name"),
            structured_info.get("location"),
            structured_info.get("current_job_title"),
            structured_info.get("preferred_job_title"),
            skills_array,
            cleaned_text,
            embedding
        ))
    conn.commit()
