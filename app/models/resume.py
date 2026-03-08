from app import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False, default="My Resume")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal Info
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    portfolio = db.Column(db.String(200))
    summary = db.Column(db.Text)

    # JSON fields for dynamic sections
    experience = db.Column(db.JSON, default=list)
    education = db.Column(db.JSON, default=list)
    skills = db.Column(db.JSON, default=list)
    projects = db.Column(db.JSON, default=list)
    certifications = db.Column(db.JSON, default=list)

    def __repr__(self):
        return f"<Resume {self.title}>"