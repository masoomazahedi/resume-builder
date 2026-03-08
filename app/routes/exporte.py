from flask import Blueprint, send_file
from flask_login import login_required, current_user
from app.models.resume import Resume
from app.services.pdf_generator import generate_pdf

export_bp = Blueprint("export", __name__)

@export_bp.route("/resume/<int:resume_id>/export")
@login_required
def export_pdf(resume_id):
    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        return "Access denied", 403

    pdf_file = generate_pdf(resume)

    filename = f"{resume.title.replace(' ', '_')}.pdf"

    return send_file(
        pdf_file,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )