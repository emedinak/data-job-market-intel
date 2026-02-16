import re

SKILLS = [
    "sql", "python", "power bi", "tableau", "excel",
    "pandas", "numpy", "spark", "databricks",
    "azure", "aws", "gcp",
    "snowflake", "dbt", "airflow",
    "git", "docker",
    "machine learning", "statistics",
    "etl", "api", "postgresql", "mysql"
]

def extract_skills(text: str):
    if not text:
        return []
    t = text.lower()
    found = []
    for s in SKILLS:
        # match palabra completa cuando aplica
        pattern = r"\b" + re.escape(s) + r"\b"
        if re.search(pattern, t):
            found.append(s)
    return sorted(set(found))
