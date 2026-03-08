from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.resume import Resume

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    if current_user.is_authenticated:
        resumes = Resume.query.filter_by(
            user_id=current_user.id
        ).order_by(Resume.updated_at.desc()).all()
        return render_template("dashboard/index.html", resumes=resumes)
    return render_template("landing.html")

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    resumes = Resume.query.filter_by(
        user_id=current_user.id
    ).order_by(Resume.updated_at.desc()).all()
    return render_template("dashboard/index.html", resumes=resumes)