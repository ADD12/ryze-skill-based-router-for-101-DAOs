import os
import sys

# Add the project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rye_router.database import SessionLocal, engine  # noqa: E402
from src.rye_router.db_models import DBTeamMember, Base  # noqa: E402


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if we already have members
    if db.query(DBTeamMember).count() == 0:
        print("Seeding initial mock data...")
        members = [
            DBTeamMember(
                user_id="u1",
                slack_id="U111",
                name="Alice",
                skills=["python", "database-admin"],
                is_available=True,
            ),
            DBTeamMember(
                user_id="u2",
                slack_id="U222",
                name="Bob",
                skills=["cuda", "python"],
                is_available=False,
            ),
            DBTeamMember(
                user_id="u3",
                slack_id="U333",
                name="Charlie",
                skills=["cesiumjs"],
                is_available=True,
            ),
        ]
        db.add_all(members)
        db.commit()
        print("Done seeding.")
    else:
        print("Database already seeded.")

    db.close()


if __name__ == "__main__":
    seed()
