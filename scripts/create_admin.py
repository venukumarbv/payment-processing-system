import os
import sys

from dotenv import load_dotenv

# This ensures that the 'src' folder is found even when running from the root

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Load environment variables from .env
load_dotenv()

# Now we can import our internal project logic
from services.api_service.src.core.security import \
    get_password_hash  # noqa:E402
from services.api_service.src.database import SessionLocal  # noqa:E402
from services.api_service.src.repository.user_repo import \
    UserRepository  # noqa:E402


def setup_admin():
    print("Starting Admin User Creation Process...")

    # 1. Create a database session
    db = SessionLocal()

    try:
        # 2. Define admin credentials
        # In a real project, these would be passed as arguments or via environment variables
        admin_username = os.getenv("ADMIN_USER_NAME")
        plain_password = os.getenv("ADMIN_PASSWORD")
        role_id = 1  # 1 = 'Admin' as per our UserRoles lookup table

        # 3. Secure the password
        # We NEVER store plain-text passwords. We use Bcrypt hashing.
        print(f"Hashing password for user: {admin_username}...")
        hashed_pw = get_password_hash(plain_password)

        # 4. Save to Database
        user_repo = UserRepository(db)

        # Check if the admin already exists to avoid Primary Key errors
        existing_user = user_repo.get_user(admin_username)
        if existing_user:
            print(f"User '{admin_username}' already exists. No action taken.")
        else:
            user_repo.create_user(admin_username, hashed_pw, role_id)
            print(f"Admin user '{admin_username}' created successfully!")
            print("Use these credentials in the /login endpoint of your API.")

    except Exception as e:
        print(f"An error occurred during admin creation: {e}")
    finally:
        # Always close the database session to release the connection
        db.close()


if __name__ == "__main__":
    setup_admin()
