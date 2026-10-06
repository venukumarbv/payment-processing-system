from sqlalchemy import text
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, username: str):
        query = text(
            "SELECT UserID, Username, HashedPassword, RoleID FROM Users WHERE Username = :uname"
        )
        return self.db.execute(query, {"uname": username}).fetchone()

    def create_user(self, username, hashed_password, role_id):
        """
        Inserts a new user into the Users table.
        Returns True if successful, False otherwise.
        """
        try:
            query = text("""
                INSERT INTO Users (Username, HashedPassword, RoleID)
                VALUES (:u, :p, :r)
            """)
            self.db.execute(
                query, {"u": username, "p": hashed_password, "r": int(role_id)}
            )
            self.db.commit()  # Commit the change to the database
            return True
        except Exception as e:
            self.db.rollback()  # Undo any partial changes if it fails
            print(f"Error creating user {username}: {e}")
            return False
