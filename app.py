from flask import Flask, request, render_template, jsonify
import re
import PyPDF2

app = Flask(__name__)

def extract_text(file_storage):
    filename = file_storage.filename
    if filename.endswith('.txt'):
        return file_storage.read().decode('utf-8')
    elif filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file_storage)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        return ""

def check_relevance(resume_text, job_desc):
    resume_text = resume_text.lower()
    job_desc = job_desc.lower()
    keywords = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_desc))
    present = [kw for kw in keywords if kw in resume_text]
    missing = [kw for kw in keywords if kw not in resume_text]
    score = int(len(present) / max(len(keywords), 1) * 100)
    message = "Good match!" if score > 60 else "Resume needs more relevant keywords."
    return {"score": score, "missing": missing, "message": message}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    file = request.files['resume']
    job_desc = request.form['job_desc']
    resume_text = extract_text(file)
    result = check_relevance(resume_text, job_desc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
