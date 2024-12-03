from groq import Groq


api_key = "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" 

client = Groq(api_key=api_key)


def analyze_responses( list_n):
    prompt = f"""
    Based on the following list of question-answer pairs, create an overall analysis of the person's performance. provide specific areas where they can improve. Offer constructive feedback in a professional tone, focusing on actionable improvements in communication, technical understanding, or any other relevant aspects and give an example of how they could have answered the questioned that were asked to them in a detailed and professional way output should be written in a way that you are giving feedback to the person the evaluation of the person should be comprehensiz.
    
    Question-Answer pairs: {list_n}
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an evaluator providing a performance review"},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",
        max_tokens=500
    )
    return chat_completion.choices[0].message.content.strip()