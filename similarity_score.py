from sentence_transformers import SentenceTransformer, util
import fitz
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

# Load models
model = SentenceTransformer('all-MiniLM-L6-v2')
nlp = spacy.load('en_core_web_sm')
job_description = """
As an AI intern at Wastelink, you'll have the opportunity to work on cutting-edge solutions. Your role will involve using your knowledge of artificial intelligence and machine learning to develop innovative tools and algorithms that will contribute to our sustainability efforts.

You will work on designing and implementing computer vision algorithms to detect and identify objects and extract specific data from them.

Responsibilities include building a prototype, data annotation, model training using frameworks like TensorFlow or PyTorch, and integration with warehouse management systems.

This is an excellent opportunity to gain hands-on experience in AI and machine learning, contributing to the automation and efficiency of our warehousing processes.

If you are a passionate and driven individual with a strong background in AI and machine learning, this internship at Wastelink is the perfect opportunity to gain hands-on experience and make a real impact in the field of sustainable waste management. Apply now and join us in shaping a cleaner and greener future!

About Company: Wastelink is a food surplus management company that helps food manufacturers manage their surplus and waste by transforming it into nutritional feeds for animals. Our mission is to supercharge the circular economy and eliminate food waste.

We process thousands of tons of food surplus into high-energy feed ingredients trusted by the world's leading feed brands while providing food manufacturers with a truly sustainable way of managing their waste.
Desired Skills and Experience
Machine Learning, Artificial Intelligence, Data Science, Deep Learning, Data Structures
"""
def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
    
    doc.close()
    return text

def extract_keywords(text):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()
    return set(keywords)

def calculate_keyword_match_score(job_keywords, resume_keywords):
    intersection = len(job_keywords.intersection(resume_keywords))
    union = len(job_keywords.union(resume_keywords))
    return intersection / union if union != 0 else 0

def extract_entities(text):
    doc = nlp(text)
    entities = {ent.text.lower() for ent in doc.ents if ent.label_ in ['ORG', 'GPE', 'PERSON', 'WORK_OF_ART', 'DATE', 'MONEY']}
    return entities

def calculate_entity_match_score(job_entities, resume_entities):
    intersection = len(job_entities.intersection(resume_entities))
    union = len(job_entities.union(resume_entities))
    return intersection / union if union != 0 else 0

def calculate_similarity_score(job_description, resume_text):
    job_embedding = model.encode(job_description, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    semantic_similarity = util.cos_sim(job_embedding, resume_embedding).item()
    
    job_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume_text)
    keyword_match_score = calculate_keyword_match_score(job_keywords, resume_keywords)
    
    job_entities = extract_entities(job_description)
    resume_entities = extract_entities(resume_text)
    entity_match_score = calculate_entity_match_score(job_entities, resume_entities)

    weight_semantic = 0.5
    weight_keyword = 0.3
    weight_entity = 0.2
    
    final_score = (weight_semantic * semantic_similarity +
                   weight_keyword * keyword_match_score +
                   weight_entity * entity_match_score)
    
    return {
        'semantic_similarity': semantic_similarity,
        'keyword_match_score': keyword_match_score,
        'entity_match_score': entity_match_score,
        'final_comprehensive_score': final_score
    }
