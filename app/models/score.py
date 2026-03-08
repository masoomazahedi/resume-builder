from app import db
from datetime import datetime

class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    rating = db.Column(db.String(20))
    breakdown = db.Column(db.JSON)
    eligibility_flags = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Score {self.total_score} for Resume {self.resume_id}>"