import requests
import json
import re

GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

PROMPT_TEMPLATE = """
You are an expert resume parser.

Extract the following fields from this resume:
- name
- location
- current job title
- preferred job title (if mentioned)
- skills (as a list)

Return the result as valid JSON in this format:
{{
  "name": "...",
  "location": "...",
  "current_job_title": "...",
  "preferred_job_title": "...",
  "skills": ["...", "..."]
}}

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

def extract_structured_info_groq(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = {
        "role": "system",
        "content": (
            "You're an AI that extracts structured info from resumes. "
            "Return ONLY a valid JSON object with the following fields:\n"
            "- name (string)\n"
            "- location (string)\n"
            "- current_job_title (string)\n"
            "- preferred_job_title (string)\n"
            "- skills (array of strings)\n\n"
            "Example:\n"
            "{\n"
            "  \"name\": \"John Doe\",\n"
            "  \"location\": \"New York, USA\",\n"
            "  \"current_job_title\": \"Software Engineer\",\n"
            "  \"preferred_job_title\": \"Senior ML Engineer\",\n"
            "  \"skills\": [\"Python\", \"Machine Learning\", \"TensorFlow\"]\n"
            "}"
        )
    }


    user_prompt = {"role": "user", "content": text[:4000]}  # Truncate for token limit

    payload = {
        "model": "llama3-8b-8192",
        "messages": [system_prompt, user_prompt],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"❌ GROQ API error {response.status_code}: {response.text}")

    data = response.json()

    if "choices" not in data:
        raise Exception(f"❌ Unexpected GROQ response: {data}")

    content = data["choices"][0]["message"]["content"]

    json_text = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_text:
        raise Exception(f"❌ Could not extract JSON block from: {content}")
    
    try:
        return json.loads(json_text.group())
    except json.JSONDecodeError:
        print("⚠️ Warning: Model did not return valid JSON. Raw:")
        print(json_text.group())
        raise Exception(f"❌ Still could not parse JSON.")

