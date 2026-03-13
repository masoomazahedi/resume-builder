# Project name: Resume-builder
app name: ResumeMind
#### Video Demo:  <[(https://www.youtube.com/watch?v=xlXNs0mW55g)]>


---

## What is ResumeMind?

Resumemind is a full-stack web application that helps job seekers build professional resumes and score them against any job description using an 8-dimension ATS (Applicant Tracking System) scoring engine.

The project was born from a real problem: **75% of resumes are rejected by automated systems before a human ever reads them.** Most people don't know why. Most tools that claim to help give vague scores with no explanation. ResumeAI was built to fix that — every lost point comes with a specific, actionable reason.

---

## Features

- **User Authentication** — Register, login, logout with secure password hashing via Werkzeug
- **Resume Builder** — Structured multi-section form covering personal info, work experience, education, skills, projects, and certifications
- **PDF Export** — Clean, ATS-safe single-column PDF using xhtml2pdf with a classinc templates
- **ATS Scoring Engine** — 8-dimension scoring system scored out of 98 points with eligibility flags
- **Two-Panel Results Report** — Separates "ATS Gaps" from "Resume Quality" feedback
- **Radar Chart Visualization** — Chart.js radar chart showing score breakdown at a glance
- **Landing Page** — Public-facing page explaining the product with a mock score preview
- **Dashboard** — Personal resume management with edit, delete, ATS score, and PDF download

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| PDF Export | xhtml2pdf |
| NLP / Scoring | Custom Python engine + spaCy |
| Frontend | Jinja2 templates, vanilla JS, CSS3 |
| Charts | Chart.js 4.4 |
| Fonts | Google Fonts — DM Serif Display + DM Sans |
| Deployment | Gunicorn-ready |

---

## Project Structure

```
resume-builder/
│
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   │
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── resume.py            # Resume model (JSON fields for dynamic sections)
│   │   └── score.py             # ATS Score model
│   │
│   ├── routes/
│   │   ├── auth.py              # /register /login /logout
│   │   ├── dashboard.py         # / and /dashboard
│   │   ├── resume.py            # /resume/new /resume/<id>/edit /resume/<id>/delete
│   │   ├── ats.py               # /resume/<id>/score
│   │   └── exporte.py           # /resume/<id>/export
│   │
│   ├── services/
│   │   ├── standards.py         # Shared dictionary — used by scorer AND CV generator
│   │   ├── keyword_extractor.py # JD parsing: tiers, intensity, synonyms, deduplication
│   │   ├── ats_scorer.py        # 8-dimension scoring engine
│   │   └── pdf_generator.py     # HTML-to-PDF conversion
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── auth/                # login.html, register.html
│   │   ├── dashboard/           # index.html
│   │   ├── resume/              # builder.html
│   │   ├── ats/                 # score_form.html, results.html
│   │   └── resume_templates/    # classic.html, masooma.html
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css
│       │   └── resume_templates/
│       │       ├── classic.css
│       │       
│       └── js/
│           └── score_chart.js
│
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

---

## Design Decisions

### Why Flask over Django?

CS50 introduced Flask as the Python web framework, and for a project of this scope Flask's simplicity is genuinely appropriate. Django's ORM, admin panel, and convention-heavy structure would have added complexity without benefit at this scale. Flask allowed full control over every layer of the application — which was important when building a custom scoring engine that needed to integrate tightly with the data model.

### Why SQLite over PostgreSQL?

For a CS50 final project running locally, SQLite eliminates setup friction entirely. The application is architected to switch to PostgreSQL for production deployment with a single environment variable change (`DATABASE_URL`). Flask-SQLAlchemy's abstraction layer makes this transparent.

### Why xhtml2pdf over WeasyPrint?

WeasyPrint requires GTK system libraries that are painful to install on Windows (the development environment for this project). xhtml2pdf works with zero system dependencies on all platforms. For a CS50 submission that a grader may run on any OS, this was the correct tradeoff.

### Why store resume sections as JSON fields?

Resume sections like work experience and education are inherently variable-length arrays. Two design options existed:

**Option A** — Separate relational tables for each section (ExperienceEntry, EducationEntry, etc.)  
**Option B** — JSON columns on the Resume model

Option A is more normalized and technically "correct" for large-scale production. Option B is faster to build, easier to query for this use case, and perfectly adequate for a single-user resume tool. The resume data is always loaded and displayed as a complete unit — never queried partially — making JSON columns the pragmatic choice.

---

## The ATS Scoring Engine — Design Process

This section documents the intellectual process behind the scoring system because it represents the most significant design challenge in the project.

### The Problem with Naive Scoring

The first instinct when building an ATS scorer is to count keyword matches:

```
score = matched_keywords / total_keywords × 100
```

This is wrong for three reasons:

1. **Broken denominator** — A job description with 100 keywords will always produce lower scores than one with 20 keywords for the same resume. The denominator is not controlled.
2. **Equal weighting** — "Python" (core technical skill) and "Jira" (workflow tool) are treated identically.
3. **No context** — "Familiar with Python" and "Architected Python microservices" score the same.

### The Iterative Design Process

The scoring system went through multiple design rounds with challenges and counter-challenges at each stage. The key decisions that emerged:

#### Decision 1 — Weighted Skill Tiers
Skills are classified into four tiers with different weights:

| Tier | Examples | Weight |
|---|---|---|
| Core Technical | Python, React, SQL | 3 |
| Infrastructure | Docker, AWS, CI/CD | 2 |
| Tools | Jira, GitHub, Figma | 1 |
| Soft Skills | Communication, Leadership | 0.5 |

**Rationale:** Missing a core technical skill is fundamentally different from missing a tool preference. A candidate without Python for a Python role is a different problem from a candidate without Jira experience.

#### Decision 2 — Requirement Intensity Detection
Job descriptions signal importance implicitly through language:

| Signal Phrase | Multiplier |
|---|---|
| "must have", "required", "mandatory" | 3× |
| "strong experience", "proficient" | 2× |
| "nice to have", "familiarity", "preferred" | 1× |

**Rationale:** "Must have Python" and "familiarity with Python" are not the same requirement. Treating them equally produces dishonest scores.

#### Decision 3 — Section Multipliers for Keyword Coverage
Where a keyword appears matters as much as whether it appears:

| Section | Multiplier |
|---|---|
| Work Experience | 1.5× |
| Projects | 1.3× |
| Skills List | 1.0× |
| Summary | 0.8× |

**Rationale:** A skill demonstrated in an experience bullet provides stronger evidence than a skill listed in a skills section. A recruiter reading the resume would draw the same inference.

#### Decision 4 — Skills Depth vs. Skills Coverage are Distinct Signals
Two separate dimensions measure different things:

- **Keyword Coverage (25 pts)** — breadth: how many JD terms appear anywhere in the resume
- **Skills Depth (18 pts)** — depth: are core skills demonstrated in experience, or just listed?

A skill mentioned only in a skills list scores 0.5. The same skill appearing in an experience bullet scores 1.0. This avoids the verbosity bias of syntactic co-occurrence patterns while still rewarding genuine demonstration over listing.

#### Decision 5 — Separate Eligibility Flags from Score

Early design capped scores when required skills were missing (score ≤ 35 if required skill absent). This was rejected because it **distorts diagnostic value**. A resume that scores 82/98 but is missing one required keyword should show 82 — not 35. The user needs to know they have a strong resume with one critical gap, not that their resume is terrible.

The solution is two separate outputs:

```
ATS Score:        82/98  ← honest scoring
Eligibility Risk: HIGH   ← separate flag
Reason:           "Python" not found in resume
```

#### Decision 6 — Recency Scoring was Rejected

A common ATS feature weights recent skills higher than older ones. This was considered and rejected for two reasons:

1. **Date parsing unreliability** — Resume dates appear in too many formats. Silent errors would apply wrong penalties without the user knowing why.
2. **Career changer discrimination** — A developer who transitioned to management and is returning to technical work would have legitimate skills penalized. The use case is too common and too harmful to ignore.

Recency is surfaced as a soft eligibility warning instead of a score modifier.

#### Decision 7 — The Human Readability Dimension
Most ATS simulators optimize only for machines. This tool adds a readability check because a resume that passes ATS but reads like a keyword dump will still be rejected by the human who reads it next. The readability dimension checks:

- Average bullet word count (ideal: 12–22 words, warning at 30+)
- Keyword density (flags stuffing above threshold)
- Verb repetition (flags when one verb dominates more than 40% of bullets)

One score is returned with granular warnings — the user sees a single number but gets specific feedback on which readability issue to fix.

### Final Scoring Model

| Dimension | Points | Primary Signal |
|---|---|---|
| Weighted Keyword Coverage | 25 | Breadth of JD term matching with section multipliers |
| Skills Depth Alignment | 18 | Core skills demonstrated in experience vs. just listed |
| Quantified Impact Quality | 15 | Metric type and scale, not just number presence |
| Seniority Alignment | 12 | Leadership verbs + scope indicators vs. JD seniority signals |
| Section Completeness | 8 | Semantic header detection, content-focused |
| Human Readability | 8 | Bullet length, keyword density, verb diversity |
| Formatting Safety | 6 | Unicode, emoji, special characters |
| Action Verb Quality | 6 | Full-bullet scan, weak verb detection |
| **Total** | **98** | |

**Why 98 and not 100?** No deterministic scoring system is 100% reliable. Presenting a maximum of 98 honest points is more trustworthy than a false ceiling of 100.

### Alignment Between Scorer and CV Generator

The scoring engine and the PDF CV generator share a single source of truth: `app/services/standards.py`. This file contains every standard both systems use — skill tiers, action verbs, section headers, formatting rules, bullet length guidelines. Any change to the standard automatically affects both the scorer and the CV output. A resume built through ResumeAI is already optimized for its own scoring system by design.

---

## How to Run

### Prerequisites
- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/resume-builder.git
cd resume-builder

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Create .env file
echo SECRET_KEY=your_secret_key_here > .env
echo DATABASE_URL=sqlite:///resume_builder.db >> .env

# Run the application
python run.py
```

Visit `http://127.0.0.1:5000`

### Generate a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Usage

1. **Register** an account at `/register`
2. **Create a resume** using the builder at `/resume/new`
3. **Export to PDF** — Classic design
4. **Score your resume** — paste any job description and run the ATS score
5. **Read the two-panel report** — fix ATS gaps first, then address readability warnings
6. **Edit and re-score** until you're satisfied with the result

---





---

*This is CS50x.*
