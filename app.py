from flask import Flask, render_template, request, jsonify
import re
import io
import pdfplumber

app = Flask(__name__)


# =========================
# SKILLS DATABASE
# =========================

SKILLS_DB = {
    "Programming": [
        "python", "java", "javascript",
        "c++", "c", "sql", "html", "css"
    ],

    "Web Development": [
        "react", "node.js", "flask",
        "django", "mongodb", "mysql"
    ],

    "AI / ML": [
        "machine learning",
        "deep learning",
        "data science",
        "tensorflow",
        "pytorch"
    ],

    "Tools": [
        "git", "github", "docker",
        "aws", "linux"
    ]
}


# =========================
# ACTION VERBS
# =========================

STRONG_ACTION_VERBS = [
    "built",
    "developed",
    "created",
    "designed",
    "implemented",
    "optimized",
    "managed",
    "improved",
    "launched"
]


# =========================
# PDF TEXT EXTRACTION
# =========================

def extract_text_from_pdf(file):
    text = ""

    try:
        file.seek(0)

        with pdfplumber.open(
            io.BytesIO(file.read())
        ) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print("PDF Error:", e)
        text = ""

    return text.strip()


# =========================
# TXT FILE EXTRACTION
# =========================

def extract_text_from_txt(file):
    text = ""

    try:
        file.seek(0)
        text = file.read().decode("utf-8", errors="ignore")

    except Exception as e:
        print("TXT Error:", e)
        text = ""

    return text.strip()


# =========================
# ANALYZE RESUME
# =========================

def analyze_resume(text):

    text_lower = text.lower()

    found_skills = {}

    for category, skills in SKILLS_DB.items():

        matched = []

        for skill in skills:
            if skill in text_lower:
                matched.append(skill)

        if matched:
            found_skills[category] = matched

    total_skills = len([
        skill
        for group in found_skills.values()
        for skill in group
    ])

    skill_score = min(100, total_skills * 8)

    found_verbs = []

    for verb in STRONG_ACTION_VERBS:
        if verb in text_lower:
            found_verbs.append(verb)

    impact_score = min(100, len(found_verbs) * 12)

    numbers = re.findall(r"\d+", text)
    quant_score = min(100, len(numbers) * 10)

    word_count = len(text.split())

    if word_count >= 200:
        length_score = 100
    else:
        length_score = 70

    ats_score = int(
        skill_score * 0.4 +
        impact_score * 0.25 +
        quant_score * 0.2 +
        length_score * 0.15
    )

    if ats_score >= 85:
        grade = "A"
    elif ats_score >= 70:
        grade = "B"
    elif ats_score >= 55:
        grade = "C"
    else:
        grade = "D"

    suggestions = []

    if skill_score < 50:
        suggestions.append("Add more technical skills")

    if impact_score < 40:
        suggestions.append("Use stronger action verbs")

    if quant_score < 30:
        suggestions.append("Add measurable achievements")

    if not suggestions:
        suggestions.append("Excellent Resume Structure")

    return {
        "overall": ats_score,
        "grade": grade,
        "word_count": word_count,
        "skills_found": found_skills,
        "action_verbs": found_verbs,
        "suggestions": suggestions
    }


# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    text = ""

    # -------------------------
    # FILE UPLOAD
    # -------------------------

    if (
        "resume_file" in request.files
        and
        request.files["resume_file"].filename
    ):

        file = request.files["resume_file"]
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file)

        elif filename.endswith(".txt"):
            text = extract_text_from_txt(file)

        else:
            return jsonify({
                "error": "Only PDF and TXT files are supported"
            }), 400

    # -------------------------
    # TEXT PASTE
    # -------------------------

    elif (
        "resume_text" in request.form
        and
        request.form["resume_text"].strip()
    ):

        text = request.form["resume_text"].strip()

    else:
        return jsonify({
            "error": "Please upload PDF/TXT or paste resume text"
        }), 400

    # -------------------------
    # SAFETY CHECK
    # -------------------------

    if len(text) < 10:
        return jsonify({
            "error": "Could not read enough resume content. Try TXT file or paste text."
        }), 400

    # -------------------------
    # FINAL ANALYSIS
    # -------------------------

    result = analyze_resume(text)

    return jsonify(result)


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)