import re
from app.services.standards import (
    ACTION_VERBS, WEAK_VERBS, SENIORITY,
    METRIC_PATTERNS, SECTION_HEADERS,
    CV_FORMATTING_STANDARDS
)
from app.services.keyword_extractor import (
    extract_keywords, normalize, resolve_synonyms
)

# ── Section multipliers for keyword scoring ──
SECTION_MULTIPLIERS = {
    "experience": 1.5,
    "projects":   1.3,
    "skills":     1.0,
    "summary":    0.8
}


def score_keyword_coverage(resume, jd_keywords):
    """
    Dimension 1 — Weighted Keyword Coverage (25 pts)
    Checks keyword presence across resume sections
    with section multipliers applied.
    """
    if not jd_keywords:
        return 25, [], []

    resume_sections = {
        "experience": " ".join([
            f"{e.get('role','')} {e.get('company','')} {e.get('description','')}"
            for e in (resume.experience or [])
        ]).lower(),
        "projects": " ".join([
            f"{p.get('title','')} {p.get('description','')} {p.get('tech_stack','')}"
            for p in (resume.projects or [])
        ]).lower(),
        "skills": " ".join(resume.skills or []).lower(),
        "summary": (resume.summary or "").lower()
    }

    total_weight = sum(k["final_weight"] for k in jd_keywords)
    matched_weight = 0
    matched_terms = []
    missing_terms = []

    for keyword in jd_keywords:
        term = resolve_synonyms(keyword["term"])
        best_match_score = 0

        for section, multiplier in SECTION_MULTIPLIERS.items():
            text = resume_sections.get(section, "")
            if term in text:
                contribution = keyword["final_weight"] * multiplier
                if contribution > best_match_score:
                    best_match_score = contribution

        if best_match_score > 0:
            matched_weight += best_match_score
            matched_terms.append(keyword["term"])
        else:
            missing_terms.append({
                "term": keyword["term"],
                "tier": keyword["tier"],
                "weight": keyword["final_weight"]
            })

    raw_score = (matched_weight / (total_weight * 1.5)) * 25
    score = min(round(raw_score, 1), 25)
    return score, matched_terms, missing_terms


def score_skills_depth(resume, jd_keywords):
    """
    Dimension 2 — Skills Depth Alignment (18 pts)
    Skills in experience/projects section score higher
    than skills only listed in skills list.
    Avoids verbosity bias by using section presence.
    """
    if not jd_keywords:
        return 18, []

    experience_text = " ".join([
        f"{e.get('description', '')} {e.get('role', '')}"
        for e in (resume.experience or [])
    ]).lower()

    project_text = " ".join([
        f"{p.get('description', '')} {p.get('tech_stack', '')}"
        for p in (resume.projects or [])
    ]).lower()

    skills_text = " ".join(resume.skills or []).lower()

    core_keywords = [k for k in jd_keywords
                     if k["tier"] in ("core_technical", "infrastructure")]

    if not core_keywords:
        return 18, []

    depth_scores = []
    weak_skills = []

    for keyword in core_keywords:
        term = resolve_synonyms(keyword["term"])
        in_experience = term in experience_text
        in_projects = term in project_text
        in_skills_list = term in skills_text

        if in_experience:
            depth_scores.append(1.0)
        elif in_projects:
            depth_scores.append(0.8)
        elif in_skills_list:
            depth_scores.append(0.5)
            weak_skills.append({
                "term": keyword["term"],
                "suggestion": f"Add '{keyword['term']}' to an experience bullet to demonstrate real usage"
            })
        else:
            depth_scores.append(0)

    avg_depth = sum(depth_scores) / len(depth_scores)
    score = round(avg_depth * 18, 1)
    return score, weak_skills


def score_quantified_impact(resume):
    """
    Dimension 3 — Quantified Impact Quality (15 pts)
    Detects metric type and scale indicators.
    """
    bullets = []
    for exp in (resume.experience or []):
        desc = exp.get("description", "")
        bullets.extend([b.strip() for b in desc.split("\n") if b.strip()])
    for proj in (resume.projects or []):
        desc = proj.get("description", "")
        bullets.extend([b.strip() for b in desc.split("\n") if b.strip()])

    if not bullets:
        return 0, []

    total_score = 0
    max_score = len(bullets) * 6  # max 6 pts per bullet (3 impact + 2 scale + 1 base)
    weak_bullets = []

    for bullet in bullets:
        bullet_lower = bullet.lower()
        bullet_score = 0

        for metric_type, data in METRIC_PATTERNS.items():
            for pattern in data["patterns"]:
                if re.search(pattern, bullet_lower):
                    bullet_score += data["weight"]
                    break

        if bullet_score == 0:
            weak_bullets.append(bullet[:80])

        total_score += bullet_score

    raw = (total_score / max_score) * 15 if max_score > 0 else 0
    score = min(round(raw, 1), 15)
    return score, weak_bullets


def score_seniority_alignment(resume, jd_text):
    """
    Dimension 4 — Seniority Alignment (12 pts)
    Detects if resume seniority level matches JD signals.
    Leadership verbs require scope indicators to count fully.
    """
    jd_lower = jd_text.lower()

    # Detect JD seniority expectation
    jd_seniority = "mid"
    if any(w in jd_lower for w in ["senior", "lead", "principal", "staff", "architect", "manager"]):
        jd_seniority = "senior"
    elif any(w in jd_lower for w in ["junior", "entry", "associate", "intern", "graduate"]):
        jd_seniority = "junior"

    # Score resume seniority signals
    experience_text = " ".join([
        f"{e.get('description', '')} {e.get('role', '')}"
        for e in (resume.experience or [])
    ]).lower()

    project_text = " ".join([
        f"{p.get('description', '')} {p.get('title', '')}"
        for p in (resume.projects or [])
    ]).lower()

    senior_signals = 0
    for verb in SENIORITY["senior"]["verbs"]:
        if verb in experience_text:
            # Require scope indicator for leadership verbs
            has_scope = any(
                s in experience_text
                for s in SENIORITY["senior"]["scope_indicators"]
            )
            senior_signals += 1.0 if has_scope else 0.5

    mid_signals = sum(
        1 for verb in SENIORITY["mid"]["verbs"]
        if verb in experience_text or verb in project_text
    )

    junior_signals = sum(
        1 for phrase in SENIORITY["junior"]["scope_indicators"]
        if phrase in experience_text or phrase in project_text
    )

    # Determine resume seniority
    if senior_signals >= 3:
        resume_seniority = "senior"
    elif mid_signals >= 3:
        resume_seniority = "mid"
    else:
        resume_seniority = "junior"

    # Score alignment
    if resume_seniority == jd_seniority:
        score = 12
    elif abs(["junior","mid","senior"].index(resume_seniority) -
             ["junior","mid","senior"].index(jd_seniority)) == 1:
        score = 7
    else:
        score = 3

    return score, jd_seniority, resume_seniority


def score_section_completeness(resume):
    """
    Dimension 5 — Section Completeness (8 pts)
    Checks all key sections have meaningful content.
    """
    score = 0
    missing = []

    checks = {
        "Contact Info": bool(resume.full_name and resume.email),
        "Work Experience": bool(resume.experience and len(resume.experience) > 0),
        "Education": bool(resume.education and len(resume.education) > 0),
        "Skills": bool(resume.skills and len(resume.skills) > 0),
        "Summary": bool(resume.summary and len(resume.summary) > 20)
    }

    weights = {
        "Contact Info": 1.5,
        "Work Experience": 2.5,
        "Education": 1.5,
        "Skills": 1.5,
        "Summary": 1.0
    }

    for section, present in checks.items():
        if present:
            score += weights[section]
        else:
            missing.append(section)

    return min(round(score, 1), 8), missing


def score_human_readability(resume):
    """
    Dimension 6 — Human Readability (8 pts)
    Checks: keyword density, bullet length, verb diversity.
    Returns one score with granular warnings.
    """
    all_bullets = []
    for exp in (resume.experience or []):
        desc = exp.get("description", "")
        all_bullets.extend([b.strip() for b in desc.split("\n") if b.strip()])
    for proj in (resume.projects or []):
        desc = proj.get("description", "")
        all_bullets.extend([b.strip() for b in desc.split("\n") if b.strip()])

    warnings = []
    score = 8

    if not all_bullets:
        return 4, ["No experience bullets found to evaluate readability"]

    # ── Bullet length check ──
    long_bullets = [b for b in all_bullets if len(b.split()) > CV_FORMATTING_STANDARDS["max_bullet_words"]]
    avg_words = sum(len(b.split()) for b in all_bullets) / len(all_bullets)

    if len(long_bullets) > len(all_bullets) * 0.3:
        score -= 2
        warnings.append(f"Too many long bullets (avg {avg_words:.0f} words). Aim for 12–22 words per bullet.")
    elif avg_words > 25:
        score -= 1
        warnings.append(f"Bullets slightly long (avg {avg_words:.0f} words). Consider tightening.")

    # ── Verb diversity check ──
    all_action_verbs = [v for group in ACTION_VERBS.values() for v in group]
    used_verbs = []
    for bullet in all_bullets:
        words = bullet.lower().split()
        for word in words[:4]:  # check first 4 words
            if word in all_action_verbs:
                used_verbs.append(word)
                break

    if used_verbs:
        from collections import Counter
        verb_counts = Counter(used_verbs)
        most_common_verb, most_common_count = verb_counts.most_common(1)[0]
        if most_common_count > len(all_bullets) * 0.4:
            score -= 1.5
            warnings.append(f"Verb repetition detected: '{most_common_verb}' used too frequently. Diversify your action verbs.")

    # ── Keyword density check ──
    all_text = " ".join(all_bullets).lower()
    words = all_text.split()
    if len(words) > 0:
        skill_mentions = sum(1 for w in words if len(w) > 3 and words.count(w) > 3)
        density = skill_mentions / len(words)
        if density > 0.15:
            score -= 1.5
            warnings.append("High keyword density detected. Resume may read unnaturally to human reviewers.")

    return max(round(score, 1), 0), warnings


def score_formatting_safety(resume):
    """
    Dimension 7 — Formatting Safety (6 pts)
    Since we control the CV template, we check
    content-level formatting issues.
    """
    all_text = " ".join([
        resume.summary or "",
        " ".join([e.get("description","") for e in (resume.experience or [])]),
        " ".join([p.get("description","") for p in (resume.projects or [])])
    ])

    score = 6
    warnings = []

    # Unicode/emoji detection
    emoji_pattern = re.compile(
        "["u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F9FF"
            u"\u2600-\u26FF""]+"
    )
    if emoji_pattern.search(all_text):
        score -= 2
        warnings.append("Emoji detected in content. ATS parsers cannot read emoji and may corrupt surrounding text.")

    # Special bullet symbols
    special_bullets = ["•", "◆", "■", "▶", "➤", "✓", "✔", "★"]
    for symbol in special_bullets:
        if symbol in all_text:
            score -= 1
            warnings.append(f"Special symbol '{symbol}' detected. Use plain text dashes or standard bullets.")
            break

    # All caps sections (hard to parse)
    caps_words = len(re.findall(r'\b[A-Z]{4,}\b', all_text))
    if caps_words > 10:
        score -= 1
        warnings.append("Excessive ALL CAPS text detected. This can confuse ATS parsers.")

    return max(round(score, 1), 0), warnings


def score_action_verbs(resume):
    """
    Dimension 8 — Action Verb Quality (6 pts)
    Full bullet scan (not just first word).
    Penalizes weak verbs.
    """
    all_action_verbs = [v for group in ACTION_VERBS.values() for v in group]
    bullets = []
    for exp in (resume.experience or []):
        desc = exp.get("description", "")
        bullets.extend([b.strip() for b in desc.split("\n") if b.strip()])

    if not bullets:
        return 0, []

    strong_count = 0
    weak_count = 0
    suggestions = []

    for bullet in bullets:
        bullet_lower = bullet.lower()
        has_strong = any(verb in bullet_lower for verb in all_action_verbs)
        has_weak = any(phrase in bullet_lower for phrase in WEAK_VERBS)

        if has_strong and not has_weak:
            strong_count += 1
        elif has_weak:
            weak_count += 1
            suggestions.append(f"Rewrite: '{bullet[:60]}...' — avoid passive phrases like 'responsible for'")
        else:
            suggestions.append(f"Strengthen: '{bullet[:60]}...' — start with an action verb")

    total = len(bullets)
    ratio = strong_count / total
    score = round(ratio * 6, 1)
    return score, suggestions


def detect_eligibility_flags(resume, jd_keywords):
    """
    Eligibility flags — separate from score.
    Hard risks that a recruiter would notice immediately.
    """
    flags = []

    must_have = [k for k in jd_keywords if k["intensity_multiplier"] == 3]
    resume_text = " ".join([
        " ".join(resume.skills or []),
        " ".join([e.get("description","") for e in (resume.experience or [])]),
        " ".join([p.get("description","") for p in (resume.projects or [])])
    ]).lower()

    for keyword in must_have:
        term = keyword["term"]
        if term not in resume_text:
            flags.append({
                "level": "CRITICAL",
                "message": f"Required skill '{keyword['term']}' not found anywhere in resume",
                "action": f"Add '{keyword['term']}' to your skills section if you have this experience"
            })

    if not resume.education:
        flags.append({
            "level": "WARNING",
            "message": "No education section found",
            "action": "Add your educational background even if it seems unrelated"
        })

    return flags


def run_ats_score(resume, jd_text):
    """
    Master scoring function.
    Returns full score breakdown + eligibility flags.
    """
    jd_keywords = extract_keywords(jd_text)

    kw_score, matched, missing         = score_keyword_coverage(resume, jd_keywords)
    depth_score, weak_skills           = score_skills_depth(resume, jd_keywords)
    impact_score, weak_bullets         = score_quantified_impact(resume)
    seniority_score, jd_level, r_level = score_seniority_alignment(resume, jd_text)
    section_score, missing_sections    = score_section_completeness(resume)
    readability_score, read_warnings   = score_human_readability(resume)
    formatting_score, format_warnings  = score_formatting_safety(resume)
    verb_score, verb_suggestions       = score_action_verbs(resume)
    eligibility_flags                  = detect_eligibility_flags(resume, jd_keywords)

    total = round(
        kw_score + depth_score + impact_score + seniority_score +
        section_score + readability_score + formatting_score + verb_score,
        1
    )

    if total >= 80:
        rating = "Excellent"
        color = "green"
    elif total >= 60:
        rating = "Good"
        color = "blue"
    elif total >= 40:
        rating = "Fair"
        color = "orange"
    else:
        rating = "Needs Work"
        color = "red"

    return {
        "total": total,
        "rating": rating,
        "color": color,
        "breakdown": {
            "keyword_coverage":   {"score": kw_score,         "max": 25, "matched": matched,        "missing": missing},
            "skills_depth":       {"score": depth_score,       "max": 18, "weak_skills": weak_skills},
            "quantified_impact":  {"score": impact_score,      "max": 15, "weak_bullets": weak_bullets},
            "seniority_alignment":{"score": seniority_score,   "max": 12, "jd_level": jd_level,     "resume_level": r_level},
            "section_completeness":{"score": section_score,    "max": 8,  "missing": missing_sections},
            "human_readability":  {"score": readability_score, "max": 8,  "warnings": read_warnings},
            "formatting_safety":  {"score": formatting_score,  "max": 6,  "warnings": format_warnings},
            "action_verbs":       {"score": verb_score,        "max": 6,  "suggestions": verb_suggestions},
        },
        "eligibility_flags": eligibility_flags,
        "jd_keywords": jd_keywords
    }