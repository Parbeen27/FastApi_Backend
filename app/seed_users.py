from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import User, Account
from auth import hash_password

# Create tables
Base.metadata.create_all(bind=engine)


def seed_users():
    db: Session = SessionLocal()
    all_users = db.query(User).all()
    print(len(all_users))

    try:
        users_data = [
            {"username": "Alice_Admin", "email": "alice.admin@test.com", "password": "Admin123!", "role": "admin"},
            {"username": "Bob_Analyst", "email": "bob.analyst@test.com", "password": "Analyst123!", "role": "analyst"},
            {"username": "Charlie_User", "email": "charlie.user@test.com", "password": "User123!", "role": "user"},
            {"username": "Diana_User", "email": "diana.user@test.com", "password": "User123!", "role": "user"},
            {"username": "Edward_User", "email": "edward.user@test.com", "password": "User123!", "role": "user"},
        ]

        for u in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == u["email"]).first()

            if existing_user:
                print(f"⚠️ User already exists: {u['email']}")
                continue

            # Create user
            new_user = User(
                email=u["email"],
                password=hash_password(u["password"]),
                role=u["role"]
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # Create account
            account = Account(
                user_id=new_user.id,
                balance=0
            )

            db.add(account)
            db.commit()

            print(f"✅ Created user + account: {u['email']}")

    except Exception as e:
        print("❌ Error:", e)
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
