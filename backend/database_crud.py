"""
crud.py — CRUD operations for AI Medical Coder Prototype
Uses models and session from database.py
"""

from database import SessionLocal, User, MedicalDocument

# --------------- CREATE ---------------

def create_user(email: str, username: str, password: str):
    """Create and store a new user"""
    with SessionLocal() as session:
        user = User(email=email, username=username)
        user.set_password(password)
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"✅ Created user: {user.username}")
        return user


def create_medical_document(user_id: str, file_name: str, parent_codes: dict, specified_codes: dict):
    """Create a new medical document record"""
    with SessionLocal() as session:
        doc = MedicalDocument(
            user_id=user_id,
            file_name=file_name,
            generated_parent_codes=parent_codes,
            generated_specified_codes=specified_codes
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        print(f"✅ Created medical document: {doc.file_name}")
        return doc


# --------------- READ (GET) ---------------

def get_user_by_email(email: str):
    """Fetch a user by email"""
    with SessionLocal() as session:
        return session.query(User).filter(User.email == email).first()


def get_all_users():
    """Get all users"""
    with SessionLocal() as session:
        return session.query(User).all()


def get_user_documents(user_id: str):
    """Get all documents uploaded by a user"""
    with SessionLocal() as session:
        return session.query(MedicalDocument).filter(MedicalDocument.user_id == user_id).all()


def get_document_by_id(doc_id: str):
    """Get a single medical document by ID"""
    with SessionLocal() as session:
        return session.query(MedicalDocument).filter(MedicalDocument.id == doc_id).first()


# --------------- UPDATE ---------------

def update_document_codes(doc_id: str, new_parent: dict, new_specified: dict):
    """Update the generated codes for a document"""
    with SessionLocal() as session:
        doc = session.query(MedicalDocument).filter(MedicalDocument.id == doc_id).first()
        if not doc:
            print("❌ Document not found.")
            return None
        doc.generated_parent_codes = new_parent
        doc.generated_specified_codes = new_specified
        session.commit()
        session.refresh(doc)
        print(f"✅ Updated document: {doc.file_name}")
        return doc


# --------------- DELETE ---------------

def delete_document(doc_id: str):
    """Delete a single document"""
    with SessionLocal() as session:
        doc = session.query(MedicalDocument).filter(MedicalDocument.id == doc_id).first()
        if doc:
            session.delete(doc)
            session.commit()
            print(f"🗑️ Deleted document: {doc.file_name}")
        else:
            print("❌ Document not found.")
