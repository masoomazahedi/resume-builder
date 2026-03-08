import re
from app.services.standards import (
    SKILL_TIERS, REQUIREMENT_INTENSITY, SYNONYMS
)

def normalize(text):
    """Lowercase, strip punctuation."""
    return re.sub(r"[^\w\s]", " ", text.lower())

def resolve_synonyms(term):
    """Return canonical form of a term."""
    term = term.lower().strip()
    for canonical, variants in SYNONYMS.items():
        if term in variants:
            return canonical
    return term

def get_skill_tier(skill):
    """Return tier name and weight for a skill."""
    skill = skill.lower()
    for tier, data in SKILL_TIERS.items():
        if skill in data["examples"]:
            return tier, data["weight"]
    return "tools", 1  # default to tools tier

def detect_intensity(sentence):
    """Detect requirement intensity of a sentence."""
    sentence = sentence.lower()
    for level, data in REQUIREMENT_INTENSITY.items():
        for phrase in data["phrases"]:
            if phrase in sentence:
                return data["multiplier"]
    return 1  # default neutral

def deduplicate_skills(skills):
    """Remove duplicate skill mentions after synonym resolution."""
    seen = set()
    unique = []
    for skill in skills:
        canonical = resolve_synonyms(skill["term"])
        if canonical not in seen:
            seen.add(canonical)
            skill["term"] = canonical
            unique.append(skill)
    return unique

def extract_keywords(jd_text):
    """
    Parse job description and return weighted keyword list.
    Each keyword has: term, tier, tier_weight, intensity_multiplier, final_weight
    """
    normalized = normalize(jd_text)
    sentences = re.split(r"[.\n]", jd_text.lower())
    keywords = []

    for tier, data in SKILL_TIERS.items():
        for skill in data["examples"]:
            if skill in normalized:
                # Find which sentence contains this skill
                intensity = 1
                for sentence in sentences:
                    if skill in sentence:
                        intensity = detect_intensity(sentence)
                        break

                keywords.append({
                    "term": skill,
                    "tier": tier,
                    "tier_weight": data["weight"],
                    "intensity_multiplier": intensity,
                    "final_weight": data["weight"] * intensity
                })

    keywords = deduplicate_skills(keywords)
    return keywords