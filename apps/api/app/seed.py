from app.db.session import SessionLocal, ensure_local_tables
from app.domains.content.seed import seed_development_content
from app.domains.creators.seed import seed_development_creator_profile


def main() -> None:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is required to seed development data")
    ensure_local_tables()
    with SessionLocal() as session:
        profiles = seed_development_creator_profile(session)
        inserted = seed_development_content(session)
    print(f"Seeded {profiles} development creator profile(s) and {inserted} development content posts.")


if __name__ == "__main__":
    main()
