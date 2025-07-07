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

def get_jd_embedding(jd_text):
    return model.encode(jd_text).tolist()

def find_filtered_matching_resumes(jd_text, job_title_filter, location_filter, skill_filter_list, top_n=10):
    jd_embedding = get_jd_embedding(jd_text)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    skills_array_str = "{" + ",".join(skill_filter_list) + "}"

    cur.execute(f"""
        SELECT id, name, current_job_title, preferred_job_title, skills,
               embedding <=> %s::vector AS similarity
        FROM resumes
        WHERE preferred_job_title ILIKE %s
          AND location ILIKE %s
          AND skills && %s::text[]
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (
        jd_embedding,
        f"%{job_title_filter}%",
        f"%{location_filter}%",
        skills_array_str,
        jd_embedding,
        top_n
    ))

    results = cur.fetchall()
    conn.close()

    if not results:
        print("No matches found for your filters.")
        return

    for i, row in enumerate(results, start=1):
        print(f"\n🔹 Match #{i}")
        print(f"Name: {row[1]}")
        print(f"Current Title: {row[2]}")
        print(f"Preferred Title: {row[3]}")
        print(f"Skills: {row[4]}")
        print(f"Similarity Score (lower is better): {row[5]:.4f}")
