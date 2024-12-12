
from groq import Groq
from langchain.prompts import ChatPromptTemplate
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

PROMPT_TEMPLATE = """
Answer the user query using only the relevant information provided to you in this prompt.

Relevant context from chat:
{relevant}

user query: {query}
"""




def ask_ques(results, user_query, messages):
    template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = template.format(
        relevant=results,
        query=user_query
    )

    client = Groq(
        api_key="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",
    )

    messages.append({"role": "user", "content": prompt})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )

    messages.pop()
    messages.append({"role": "user", "content": user_query})
    messages.append({"role": "assistant", "content": chat_completion.choices[0].message.content})

    return chat_completion.choices[0].message.content
