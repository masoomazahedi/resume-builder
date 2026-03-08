from flask import render_template, current_app
from xhtml2pdf import pisa
import io
import os

def generate_pdf(resume):
    # Read CSS file and pass it into the template
    css_path = os.path.join(
        current_app.static_folder, "css", "resume_templates", "classic-design.css"
    )
    with open(css_path, "r") as f:
        css = f.read()

    html_content = render_template(
        "resume_templates/classic.html",
        resume=resume,
        css=css
    )

    pdf_file = io.BytesIO()
    pisa.CreatePDF(src=html_content, dest=pdf_file, encoding="utf-8")
    pdf_file.seek(0)

    return pdf_file