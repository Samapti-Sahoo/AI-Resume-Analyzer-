from flask import Flask, render_template, request, jsonify
import re
import io
import pdfplumber
import pytesseract

from pdf2image import convert_from_bytes

app = Flask(__name__)

# IMPORTANT:
# Change this path if needed

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


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


STRONG_ACTION_VERBS = [
    "built", "developed", "created",
    "designed", "implemented",
    "optimized", "managed",
    "improved", "launched"
]


# =========================
# OCR PDF EXTRACTION
# =========================

def extract_text_from_pdf(file):

    text = ""

    try:
        file.seek(0)
        pdf_bytes = file.read()

        # First try normal extraction

        with pdfplumber.open(
            io.BytesIO(pdf_bytes)
        ) as pdf:

            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        # If failed → OCR fallback

        if len(text.strip()) < 30:

            print("Using OCR fallback...")

            images = convert_from_bytes(pdf_bytes)

            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"

    except Exception as e:
        print("OCR Error:", e)
        text = ""

    return text.strip()


# =========================
# ANALYSIS
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

    if word_count >= 250:
        length_score = 100
    else:
        length_score = 60

    ats_score = int(
        skill_score * 0.4 +
        impact_score * 0.25 +
        quant_score * 0.2 +
        length_score * 0.15
    )

    suggestions = []

    if skill_score < 50:
        suggestions.append(
            "Add more technical skills"
        )

    if impact_score < 40:
        suggestions.append(
            "Use stronger action verbs"
        )

    if quant_score < 30:
        suggestions.append(
            "Add measurable achievements"
        )

    if not suggestions:
        suggestions.append(
            "Excellent Resume Structure"
        )

    return {
        "overall": ats_score,
        "word_count": word_count,
        "skills_found": found_skills,
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

    if (
        "resume_file" in request.files
        and
        request.files["resume_file"].filename
    ):

        file = request.files["resume_file"]

        text = extract_text_from_pdf(file)

        print("TEXT LENGTH:", len(text))

    elif (
        "resume_text" in request.form
        and
        request.form["resume_text"].strip()
    ):

        text = request.form["resume_text"].strip()

    else:
        return jsonify({
            "error":
            "Please upload resume or paste text"
        }), 400

    if len(text) < 30:
        return jsonify({
            "error":
            "Resume content too short"
        }), 400

    result = analyze_resume(text)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)