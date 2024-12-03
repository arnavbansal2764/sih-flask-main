from flask import Flask, request, jsonify
import PyPDF2
from groq import Groq
from controllers.verifyUrl import is_valid_url 
from utils.download_pdf import download_pdf
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.secure_api_call import exponential_backoff_request
from similarity_score import pdf_to_text, calculate_similarity_score
from resume_builder import resume_builder
from recommendation import generate_recommendation
import requests
from pydub import AudioSegment
import speech_recognition as sr
import asyncio
from hume import HumeStreamClient
from hume.models.config import ProsodyConfig

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])
class InterviewAssistant:
    def __init__(self, api_key, pdf_path=None):
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        
        if pdf_path: 
            self.resume = self.extract_text_from_pdf(pdf_path)
        else:
            self.resume = ""  

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def generate_questions(self):
        prompt = f"Generate 5-10 concise and formal technical questions based on the following resume: {self.resume}"
        
        def api_call():
            return self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an interviewer who asks only formal and concise questions."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                max_tokens=150
            )

        chat_completion = exponential_backoff_request(api_call) 
        return chat_completion.choices[0].message.content.strip().split('\n')

    def analyze_response(self, question, transcript):
        prompt = f"Based on the question: '{question}', evaluate the response: '{transcript}' and provide constructive feedback."
        
        def api_call():
            return self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an evaluator who gives constructive feedback on interview responses."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",
                max_tokens=150
            )

        chat_completion = exponential_backoff_request(api_call) 
        return chat_completion.choices[0].message.content.strip()

@app.route('/ask_questions', methods=['POST'])
@limiter.limit("10 per minute")
def ask_questions():
    data = request.json
    pdf_url = data.get('pdf_url')

    if not pdf_url or not is_valid_url(pdf_url):
        return jsonify({"error": "Invalid or missing PDF URL"}), 400
    
    pdf_path = 'temp_resume.pdf'
    try:
        download_result = download_pdf(pdf_url, pdf_path)
        if "error" in download_result:
            return jsonify(download_result), 400

        api_key = "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" 
        assistant = InterviewAssistant(api_key, pdf_path)
    
        questions = assistant.generate_questions()
        return jsonify({"questions": questions})
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route('/analyze_responses', methods=['POST'])
def analyze_responses():
    data = request.json
    responses = data.get('responses')  

    if not responses:
        return jsonify({"error": "Responses data is required"}), 400

    api_key = "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" 
    assistant = InterviewAssistant(api_key, pdf_path=None)

    analysis_results = []  

    for item in responses:
        question = item.get('question')
        transcript = item.get('transcript')

        if not question or not transcript:
            return jsonify({"error": "Both question and transcript are required for each response"}), 400

        feedback = assistant.analyze_response(question, transcript)

        analysis_result = {
            "question": question,
            "transcript": transcript,
            "feedback": feedback
        }
        analysis_results.append(analysis_result)

    return jsonify({"analysis_results": analysis_results})

@app.route('/similarity-score', methods=['POST'])
def similarity_score():
    data = request.json
    pdf_url = data.get('pdf_url')
    job_description = data.get('job_description')
    if not pdf_url:
        return jsonify({'error': 'PDF URL is required'}), 400
    pdf_path = 'downloaded_resume.pdf'
    
    if not download_pdf(pdf_url, pdf_path):
        return jsonify({'error': 'Failed to download PDF'}), 500
    resume_text = pdf_to_text(pdf_path)
    scores = calculate_similarity_score(resume_text,job_description)

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

@app.route('/cultural-fit', methods=['POST'])


if __name__ == "__main__":
    app.run(debug=True)