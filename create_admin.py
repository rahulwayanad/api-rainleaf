"""
Run once to create the admin user:
    python create_admin.py
"""
from database import SessionLocal, engine
import models
from auth import hash_password

models.Base.metadata.create_all(bind=engine)

USERNAME = "admin"
EMAIL = "admin@rainleafresort.com"
PASSWORD = "admin123"   # Change this after first login

db = SessionLocal()

existing = db.query(models.User).filter(models.User.username == USERNAME).first()
if existing:
    print(f"Admin user '{USERNAME}' already exists.")
else:
    user = models.User(
        username=USERNAME,
        email=EMAIL,
        hashed_password=hash_password(PASSWORD),
    )
    db.add(user)
    db.commit()
    print(f"Admin user '{USERNAME}' created successfully.")
    print(f"Login with username='{USERNAME}' and password='{PASSWORD}'")

db.close()
