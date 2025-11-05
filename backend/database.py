"""
database.py  —  Database configuration and ORM models
Compatible with SQLite now, easily portable to MSSQL later.
"""

import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, String, ForeignKey, event, JSON
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from passlib.hash import bcrypt

# ------------- Load environment variables -------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_medical_coder.db")

# ------------- Base ORM class -------------
Base = declarative_base()

# ------------- Engine Creation -------------
# SQLite engine will create a local .db file automatically
# MSSQL / PostgreSQL will just work when you change DATABASE_URL
engine = create_engine(
    DATABASE_URL,
    echo=True,          # logs SQL in console
    future=True,
)

# Enable foreign keys in SQLite (disabled by default)
@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    except Exception:
        pass

# ------------- Session Factory -------------
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# =====================================================
#                     MODELS
# =====================================================

class User(Base):
    """Stores user credentials and metadata"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, nullable=False)

    # Relationships
    documents = relationship(
        "MedicalDocument",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Helper methods
    def set_password(self, password: str):
        """Hash and set a user's password"""
        # Prevent overly long passwords (>72 bytes for bcrypt)
        password = password[:72]
        self.password_hash = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify a plain password against stored hash"""
        return bcrypt.verify(password, self.password_hash)


class MedicalDocument(Base):
    """Stores each uploaded file with its generated codes"""
    __tablename__ = "medical_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String, nullable=False)

    # Store code results as JSON
    generated_parent_codes = Column(JSON, nullable=True)
    generated_specified_codes = Column(JSON, nullable=True)

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationship back to User
    user = relationship("User", back_populates="documents")


# =====================================================
#                 INITIALIZATION
# =====================================================
def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully.")


# =====================================================
#                 MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    init_db()
    # Uncomment below to test
    # test_insert()
