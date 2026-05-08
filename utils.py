import PyPDF2


def extract_text_from_pdf(file):

    text = ""

    pdf_reader = PyPDF2.PdfReader(file)

    for page in pdf_reader.pages:
        text += page.extract_text()

    return text


def extract_skills(text):

    skills_list = [
        "python",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "sql",
        "machine learning",
        "deep learning",
        "data science",
        "flask",
        "django",
        "streamlit",
        "react",
        "nodejs",
        "mongodb",
        "mysql",
        "git",
        "github",
        "aws"
    ]

    found_skills = []

    text = text.lower()

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)

    return found_skills