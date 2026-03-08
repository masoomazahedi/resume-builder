# ─────────────────────────────────────────────
# SHARED STANDARDS — used by BOTH scorer and CV generator
# Any change here affects both systems simultaneously
# ─────────────────────────────────────────────

# ── Skill Tier Classification ──
SKILL_TIERS = {
    "core_technical": {
        "weight": 3,
        "examples": [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby",
            "go", "rust", "swift", "kotlin", "sql", "r", "scala", "php",
            "react", "angular", "vue", "node", "django", "flask", "spring",
            "tensorflow", "pytorch", "machine learning", "deep learning",
            "data science", "nlp", "computer vision", "algorithms"
        ]
    },
    "infrastructure": {
        "weight": 2,
        "examples": [
            "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
            "ansible", "jenkins", "ci/cd", "linux", "nginx", "redis",
            "postgresql", "mongodb", "mysql", "elasticsearch", "kafka",
            "rabbitmq", "graphql", "rest", "restful", "microservices"
        ]
    },
    "tools": {
        "weight": 1,
        "examples": [
            "git", "github", "gitlab", "jira", "confluence", "figma",
            "postman", "vs code", "intellij", "slack", "notion", "trello"
        ]
    },
    "soft_skills": {
        "weight": 0.5,
        "examples": [
            "communication", "leadership", "teamwork", "problem solving",
            "critical thinking", "collaboration", "time management",
            "adaptability", "creativity", "mentoring"
        ]
    }
}

# ── Requirement Intensity Signals ──
REQUIREMENT_INTENSITY = {
    "must_have": {
        "multiplier": 3,
        "phrases": [
            "must have", "required", "minimum requirement", "mandatory",
            "you must", "essential", "you will need", "necessary"
        ]
    },
    "strong": {
        "multiplier": 2,
        "phrases": [
            "strong experience", "proficient", "solid understanding",
            "extensive experience", "expert", "proven experience",
            "deep knowledge", "advanced"
        ]
    },
    "preferred": {
        "multiplier": 1,
        "phrases": [
            "nice to have", "preferred", "bonus", "plus", "familiarity",
            "exposure to", "knowledge of", "ideally", "desirable",
            "advantage if"
        ]
    }
}

# ── Synonym Dictionary ──
SYNONYMS = {
    "javascript": ["js", "es6", "ecmascript", "node.js", "nodejs"],
    "python": ["py"],
    "machine learning": ["ml", "ai", "artificial intelligence"],
    "kubernetes": ["k8s"],
    "continuous integration": ["ci/cd", "ci", "cd", "devops pipeline"],
    "rest": ["restful", "rest api", "http api"],
    "postgresql": ["postgres", "psql"],
    "mongodb": ["mongo"],
    "amazon web services": ["aws", "amazon cloud"],
    "google cloud": ["gcp", "google cloud platform"],
    "react": ["reactjs", "react.js"],
    "vue": ["vuejs", "vue.js"],
    "angular": ["angularjs"],
    "docker": ["container", "containerization", "containerized"],
    "version control": ["git", "github", "gitlab", "bitbucket"],
}

# ── Strong Action Verbs ──
ACTION_VERBS = {
    "leadership": [
        "led", "managed", "directed", "spearheaded", "oversaw",
        "supervised", "mentored", "coordinated", "guided", "headed"
    ],
    "achievement": [
        "achieved", "delivered", "exceeded", "launched", "grew",
        "increased", "improved", "boosted", "accelerated", "drove"
    ],
    "technical": [
        "built", "developed", "engineered", "architected", "implemented",
        "designed", "deployed", "automated", "migrated", "optimized",
        "refactored", "integrated", "scaled", "containerized"
    ],
    "analytical": [
        "analyzed", "evaluated", "identified", "measured", "researched",
        "diagnosed", "assessed", "investigated", "modeled", "forecasted"
    ],
    "collaborative": [
        "collaborated", "partnered", "contributed", "supported",
        "facilitated", "presented", "negotiated", "aligned"
    ]
}

WEAK_VERBS = [
    "helped", "assisted", "worked on", "participated", "was responsible",
    "responsible for", "involved in", "tasked with", "handled"
]

# ── Seniority Signals ──
SENIORITY = {
    "senior": {
        "verbs": ["led", "architected", "spearheaded", "directed",
                  "managed", "oversaw", "designed", "established"],
        "scope_indicators": [
            "team of", "engineers", "stakeholders", "cross-functional",
            "production", "enterprise", "multi-region", "organization",
            "company-wide", "million", "billion", "thousands"
        ]
    },
    "mid": {
        "verbs": ["built", "developed", "implemented", "optimized",
                  "deployed", "integrated", "delivered", "contributed"],
        "scope_indicators": [
            "users", "requests", "services", "systems",
            "features", "modules", "pipelines"
        ]
    },
    "junior": {
        "verbs": ["assisted", "supported", "helped", "learned",
                  "familiar", "exposure", "participated"],
        "scope_indicators": [
            "class project", "coursework", "bootcamp",
            "personal project", "university", "student"
        ]
    }
}

# ── Quantification Patterns ──
METRIC_PATTERNS = {
    "performance": {
        "weight": 3,
        "patterns": [r"\d+%", r"\d+x\s*(faster|improvement|better)",
                     r"reduced.*by", r"improved.*by", r"increased.*by",
                     r"\d+\s*ms", r"latency", r"throughput"]
    },
    "revenue": {
        "weight": 3,
        "patterns": [r"\$\d+", r"revenue", r"cost\s*saving",
                     r"budget", r"roi", r"profit"]
    },
    "scale": {
        "weight": 2,
        "patterns": [r"\d+[km]?\s*users", r"\d+[km]?\s*requests",
                     r"million", r"billion", r"transactions",
                     r"data.*[tgm]b", r"daily active"]
    },
    "efficiency": {
        "weight": 2,
        "patterns": [r"automated", r"eliminated", r"streamlined",
                     r"saved.*hours", r"\d+\s*hours"]
    },
    "team": {
        "weight": 1,
        "patterns": [r"team of \d+", r"\d+ engineers",
                     r"\d+ developers", r"\d+ members"]
    }
}

# ── Section Headers (semantic detection) ──
SECTION_HEADERS = {
    "experience": [
        "experience", "work experience", "professional experience",
        "employment", "career history", "work history", "positions held"
    ],
    "education": [
        "education", "academic background", "qualifications",
        "academic qualifications", "degrees"
    ],
    "skills": [
        "skills", "technical skills", "core competencies",
        "tech stack", "technologies", "competencies", "expertise"
    ],
    "projects": [
        "projects", "personal projects", "key projects",
        "portfolio", "selected projects"
    ],
    "summary": [
        "summary", "professional summary", "profile",
        "objective", "about me", "overview"
    ]
}

# ── ATS-Safe Formatting Rules (CV Generator alignment) ──
# These rules define what our CV template must follow
# to guarantee a high formatting safety score
CV_FORMATTING_STANDARDS = {
    "single_column": True,          # No multi-column layouts
    "standard_fonts": True,         # No decorative/icon fonts
    "no_tables": True,              # No HTML tables for layout
    "no_images": True,              # No profile photos or icons
    "unicode_safe": True,           # No emoji or special symbols
    "standard_headers": True,       # Use headers from SECTION_HEADERS
    "bullet_word_range": (12, 22),  # Ideal bullet length
    "max_bullet_words": 30          # Hard warning threshold
}