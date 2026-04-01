import re
import PyPDF2

# 🔹 Extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    
    return text


# 🔹 Load skills dataset
def load_skills():
    skills = set()
    with open("skills.txt", "r") as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                skills.add(line)
    return skills


# 🔹 Clean text
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text


# 🔹 Extract skills from text
def extract_skills(text, skills_db):
    words = text.split()
    extracted = set()

    for i in range(len(words)):
        if words[i] in skills_db:
            extracted.add(words[i])

        if i < len(words) - 1:
            two_word = words[i] + " " + words[i+1]
            if two_word in skills_db:
                extracted.add(two_word)

    return extracted


# 🔹 Match logic
def match_resume_jd(resume_text, jd_text):
    skills_db = load_skills()

    resume_clean = preprocess(resume_text)
    jd_clean = preprocess(jd_text)

    resume_skills = extract_skills(resume_clean, skills_db)
    jd_skills = extract_skills(jd_clean, skills_db)

    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills - resume_skills

    if len(jd_skills) == 0:
        score = 0
    else:
        score = round((len(matched) / len(jd_skills)) * 100, 2)

    return score, matched, missing