from .config import require_env, RESULTS_PER_PAGE
from .adzuna_client import AdzunaClient

def main():
    require_env()
    client = AdzunaClient()

    print("Calling Adzuna API...")
    data = client.search_jobs("data analyst", page=1, results_per_page=RESULTS_PER_PAGE)

    print("✅ Response received")
    print("Keys:", list(data.keys()))

    count = data.get("count")
    results = data.get("results", [])

    print("Total matches (count):", count)
    print("Results returned:", len(results))

    if results:
        r0 = results[0]
        print("\n--- Example job ---")
        print("Title:", r0.get("title"))
        print("Company:", (r0.get("company") or {}).get("display_name"))
        print("Location:", (r0.get("location") or {}).get("display_name"))
        print("URL:", r0.get("redirect_url") or r0.get("adref"))

if __name__ == "__main__":
    main()
