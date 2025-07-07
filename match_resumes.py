from utils.matching import find_filtered_matching_resumes

if __name__ == "__main__":
    jd = """
    Looking for a Data Scientist experienced in Python, SQL, and machine learning.
    Must be based in Delhi or open to relocation.
    """
    find_filtered_matching_resumes(
        jd_text=jd,
        job_title_filter="Data Scientist",
        location_filter="Delhi",
        skill_filter_list=["Python", "SQL", "machine learning"]
    )
