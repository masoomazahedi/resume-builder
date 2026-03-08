from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.resume import Resume
import json

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume/new", methods=["GET", "POST"])
@login_required
def new_resume():
    if request.method == "POST":
        resume = Resume(
            user_id=current_user.id,
            title=request.form.get("title", "My Resume"),
            full_name=request.form.get("full_name"),
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            linkedin=request.form.get("linkedin"),
            github=request.form.get("github"),
            portfolio=request.form.get("portfolio"),
            summary=request.form.get("summary"),
            experience=json.loads(request.form.get("experience", "[]")),
            education=json.loads(request.form.get("education", "[]")),
            skills=json.loads(request.form.get("skills", "[]")),
            projects=json.loads(request.form.get("projects", "[]")),
            certifications=json.loads(request.form.get("certifications", "[]")),
        )
        db.session.add(resume)
        db.session.commit()
        flash("Resume saved successfully!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("resume/builder.html")


@resume_bp.route("/resume/<int:resume_id>/edit", methods=["GET", "POST"])
@login_required
def edit_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        resume.title = request.form.get("title", resume.title)
        resume.full_name = request.form.get("full_name")
        resume.email = request.form.get("email")
        resume.phone = request.form.get("phone")
        resume.linkedin = request.form.get("linkedin")
        resume.github = request.form.get("github")
        resume.portfolio = request.form.get("portfolio")
        resume.summary = request.form.get("summary")
        resume.experience = json.loads(request.form.get("experience", "[]"))
        resume.education = json.loads(request.form.get("education", "[]"))
        resume.skills = json.loads(request.form.get("skills", "[]"))
        resume.projects = json.loads(request.form.get("projects", "[]"))
        resume.certifications = json.loads(request.form.get("certifications", "[]"))

        db.session.commit()
        flash("Resume updated!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("resume/builder.html", resume=resume)


@resume_bp.route("/resume/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.index"))

    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted.", "info")
    return redirect(url_for("dashboard.index"))