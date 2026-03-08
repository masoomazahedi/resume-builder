from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.resume import Resume
from app.models.score import Score
from app.services.ats_scorer import run_ats_score

ats_bp = Blueprint("ats", __name__)

@ats_bp.route("/resume/<int:resume_id>/score", methods=["GET", "POST"])
@login_required
def score_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        jd_text = request.form.get("job_description", "").strip()

        if len(jd_text) < 50:
            flash("Please paste a full job description (at least 50 characters).", "danger")
            return render_template("ats/score_form.html", resume=resume)

        result = run_ats_score(resume, jd_text)

        # Save score to DB
        score = Score(
            resume_id=resume.id,
            job_description=jd_text,
            total_score=result["total"],
            rating=result["rating"],
            breakdown=result["breakdown"],
            eligibility_flags=result["eligibility_flags"]
        )
        db.session.add(score)
        db.session.commit()

        return render_template("ats/results.html", resume=resume, result=result, score=score)

    return render_template("ats/score_form.html", resume=resume)