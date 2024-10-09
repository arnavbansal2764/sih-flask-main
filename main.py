from flask import Flask, request, jsonify
import requests
import os
from similarity_score import pdf_to_text, calculate_similarity_score
from resume_builder import resume_builder
from recommendation import generate_recommendation

app = Flask(__name__)

def download_pdf(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    return False

@app.route('/similarity-score', methods=['POST'])
def similarity_score():
    data = request.json
    pdf_url = data.get('pdf_url')
    if not pdf_url:
        return jsonify({'error': 'PDF URL is required'}), 400
    pdf_path = 'downloaded_resume.pdf'
    
    if not download_pdf(pdf_url, pdf_path):
        return jsonify({'error': 'Failed to download PDF'}), 500
    resume_text = pdf_to_text(pdf_path)
    scores = calculate_similarity_score(resume_text)

    os.remove(pdf_path)

    return jsonify(scores)

@app.route('/resume-build', methods=['POST'])
def build_resume():
    data = request.json
    resume_url = data.get('resume_url')
    job_description = data.get('job_description')
    pdf_path = 'downloaded_resume.pdf'
    
    if not download_pdf(resume_url, pdf_path):
        return jsonify({'error': 'Failed to download PDF'}), 500
    resume_text = pdf_to_text(pdf_path)
    if not resume_text or not job_description:
        return jsonify({'error': 'Both resume text and job description are required.'}), 400

    generated_resume = resume_builder(resume_text, job_description)
    return jsonify({'generated_resume': generated_resume})

@app.route('/recommendation', methods=['POST'])
def recommendation():
    data = request.json
    resume_url = data.get('resume_url')
    job_description = data.get('job_description')
    pdf_path = 'downloaded_resume.pdf'
    if not resume_url or not job_description:
        return jsonify({'error': 'Both resume URL and job description are required.'}), 400
    if not download_pdf(resume_url, pdf_path):
        return jsonify({'error': 'Failed to download PDF'}), 500
    resume_text = pdf_to_text(pdf_path)
    try:
        response = generate_recommendation(resume_text, job_description)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
