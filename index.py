import json
import redis
import os
from cult import cultural_fit
from similarity_score import pdf_to_text, calculate_similarity_score
from resume_builder import resume_builder
from recommendation import generate_recommendation
from interview import InterviewAssistant
import requests


redisClient = redis.Redis()

def download_pdf(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    return False


api_key = "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"

print("RUNNING: REDIS AI BACKEND")

while True:
    try:
        response = redisClient.rpop("messages")
        if response:
            print("hello\n")
            res = json.loads(response)
            print("hello2\n")
            clientId = res['clientId']
            message = res['message']  # No need to load it again
            type = message['type']
            data = message['data']
            
            print(json.dumps(data, indent=4))
            if type == "GET_RECOMMENDATION":
                job_description = data.get('job_description')
                resume = data.get('resume')
                if not resume or not job_description:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Job Description and Resume Absent"}))
                    continue
                try:
                    pdf_path = 'downloaded_resume.pdf'
                    if not download_pdf(resume, pdf_path):
                        redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Not able to download PDF"}))
                        continue
                    resume_text = pdf_to_text(pdf_path)
                    recommendation = generate_recommendation(resume_text,job_description)
                    os.remove(pdf_path)
                    similarity_score_json = {
                        "type": "RECOMMENDATION",
                        "payload": {
                            "recommendation": recommendation
                        }
                    }
                    json_string = json.dumps(similarity_score_json)
                    redisClient.publish(clientId,json_string)
                except Exception as e:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "Not able to download PDF"}}))
                pass
            elif type == "GET_RESUME_BUILD":
                job_description = data.get('job_description')
                resume = data.get('resume')
                if not resume or not job_description:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Job Description and Resume Absent"}))
                    continue
                try:
                    pdf_path = 'downloaded_resume.pdf'
                    if not download_pdf(resume, pdf_path):
                        redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Not able to download PDF"}))
                        continue
                    resume_text = pdf_to_text(pdf_path)
                    
                    resume_built = resume_builder(resume_text,job_description)
                    os.remove(pdf_path)
                    resume_json = json.dumps({
                        "type": "RESUME_BUILD",
                        "payload": {
                            "resume": resume_built
                        }
                    })
                    redisClient.publish(clientId,resume_json)
                except Exception as e:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "Not able to download PDF"}}))
                pass
            elif type == "GET_SIMILARITY_SCORE":
                
                job_description = data.get('job_description')
                resume = data.get('resume')
                if not resume or not job_description:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Job Description and Resume Absent"}))
                    continue
                try:
                    pdf_path = 'downloaded_resume.pdf'
                    if not download_pdf(resume, pdf_path):
                        redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Not able to download PDF"}))
                        continue
                        
                    resume_text = pdf_to_text(pdf_path)
                    score = calculate_similarity_score(resume_text,job_description)
                    os.remove(pdf_path)
                    score_json = json.dumps({
                        "type": "SIMILARITY_SCORE",
                        "payload": {
                            "score": score
                        }
                    })
                    redisClient.publish(clientId,score_json)
                except Exception as e:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "Not able to download PDF"}}))
                pass
            elif type == "GET_QUESTIONS":
                resume = data.get('resume')
                if not resume:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Resume Absent"}))
                    continue
                try:
                    pdf_path = 'downloaded_resume.pdf'
                    if not download_pdf(resume, pdf_path):
                        redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Not able to download PDF"}))
                        continue
                    assistant = InterviewAssistant(api_key=api_key, pdf_path=pdf_path)    
                    questions = assistant.generate_questions()
                    #questions = ["What is your name?", "What is your experience?", "What are your skills?"]
                    os.remove(pdf_path)
                    score_json = json.dumps({
                        "type": "SIMILARITY_SCORE",
                        "payload": {
                            "questions": questions
                        }
                    })
                    redisClient.publish(clientId,score_json)
                    print("published")
                except Exception as e:
                    print(e)
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "An Error Occurred"}}))
                pass
            elif type == "GET_INTERVIEW_ANALYSIS":
                question_responses = data.get('question_responses')
                if not question_responses:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "message": "Question Responses Absent"}))
                    continue
                try:
                    print("hello in here")
                    assistant = InterviewAssistant()
                    analysis_results = []  

                    for item in question_responses:
                        question = item.get('question')
                        transcript = item.get('transcript')

                        if not question or not transcript:
                            continue

                        feedback = assistant.analyze_response(question, transcript)

                        analysis_result = {
                            "question": question,
                            "transcript": transcript,
                            "feedback": feedback
                        }
                        analysis_results.append(analysis_result)

                    analysis_result_json = json.dumps(analysis_result)
                    score_json = json.dumps({
                        "type": "INTERVIEW_ANALYSIS",
                        "payload": {
                            "analysis": analysis_result_json
                        }
                    })
                    redisClient.publish(clientId,score_json)
                    print("published")
                except Exception as e:
                    print(e)
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "An Error Occurred"}}))
                pass
            elif type == "GET_CULTURAL_FIT":
                print("here in fit")
                audio_url = data.get('audio_url')
                if not audio_url:
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "An Error Occurred"}}))
                    continue
                try:
                    culture_fit_score = cultural_fit(audio_url)
                    redisClient.publish(clientId,culture_fit_score)
                    print("published")
                except Exception as e:
                    print(e)
                    redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "An Error Occurred"}}))
                pass
    except Exception as e:
        print(e)
        redisClient.publish(clientId,json.dumps({"type": "ERROR", "payload": {"message": "Not able to download PDF"}}))