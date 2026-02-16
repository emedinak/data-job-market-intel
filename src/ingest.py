from .config import require_env, DB_PATH, KEYWORDS, RESULTS_PER_PAGE
from .adzuna_client import AdzunaClient
from .db import get_engine, init_db, get_session, Job

def pick(d: dict, path: str, default=None):
    # path like "company.display_name"
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(part)
        if cur is None:
            return default
    return cur

def ingest(max_pages_per_keyword: int = 3):
    require_env()
    client = AdzunaClient()

    engine = get_engine(DB_PATH)
    init_db(engine)
    session = get_session(engine)

    inserted = 0
    skipped = 0

    for kw in KEYWORDS:
        for page in range(1, max_pages_per_keyword + 1):
            data = client.search_jobs(kw, page=page, results_per_page=RESULTS_PER_PAGE)
            results = data.get("results", []) or []
            if not results:
                break

            for r in results:
                job_id = r.get("id")
                if not job_id:
                    continue

                if session.get(Job, job_id):
                    skipped += 1
                    continue

                job = Job(
                    id=job_id,
                    title=r.get("title"),
                    company=pick(r, "company.display_name"),
                    location=pick(r, "location.display_name"),
                    category=pick(r, "category.label"),
                    created=r.get("created"),
                    description=r.get("description"),
                    url=r.get("redirect_url") or r.get("adref"),
                    salary_min=r.get("salary_min"),
                    salary_max=r.get("salary_max"),
                    salary_is_predicted=1 if r.get("salary_is_predicted") else 0,
                    salary_interval=r.get("salary_interval"),
                    currency=r.get("currency"),
                )

                session.add(job)
                inserted += 1

            session.commit()

    session.close()
    print(f"✅ Ingest done | inserted={inserted} | skipped(existing)={skipped} | db={DB_PATH}")

if __name__ == "__main__":
    ingest(max_pages_per_keyword=25)