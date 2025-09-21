
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
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Automated Resume Relevance Check System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 600px; margin: auto; }
        .result { margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 4px; }
    </style>
</head>
<body>
<div class="container">
    <h2>Automated Resume Relevance Check System</h2>
    <form id="resumeForm">
        <label>Upload Resume (Text or PDF):</label><br>
        <input type="file" id="resumeFile" accept=".txt,.pdf" required><br><br>
        <label>Paste Job Description:</label><br>
        <textarea id="jobDesc" rows="6" cols="60" required></textarea><br><br>
        <button type="submit">Check Relevance</button>
    </form>
    <div class="result" id="result"></div>
</div>
<script>
document.getElementById('resumeForm').onsubmit = async function(e) {
    e.preventDefault();
    const file = document.getElementById('resumeFile').files[0];
    const jobDesc = document.getElementById('jobDesc').value;
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_desc', jobDesc);

    const res = await fetch('/check', {method: 'POST', body: formData});
    const data = await res.json();
    document.getElementById('result').innerHTML =
        `<strong>Relevance Score:</strong> ${data.score}%<br>
         <strong>Missing Keywords:</strong> ${data.missing.join(', ') || 'None'}<br>
         <strong>Message:</strong> ${data.message}`;
};
</script>
</body>
</html>
