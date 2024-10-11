# sih-flask-main

## Similarity Score 
### Endpoint: `/similarity-score`

### Method: `POST`

### Request Body:
The request body should be a JSON object containing a `pdf_url` key with the link to the PDF file you want to analyze.

**Example Request JSON:**

```json
{
  "pdf_url": "https://utfs.io/f/uYCJGxAcJId8uk6is3AcJId8F3SNyhRlvDtHqWgfLOrVjk70"
}
```



**Example Response JSON:**

```json
{
  "entity_match_score": 0.03125,
  "final_comprehensive_score": 0.186464498256216,
  "keyword_match_score": 0.06291390728476821,
  "semantic_similarity": 0.32268065214157104
}
```

## Resume Builder
### Endpoint: `/resume-build`

### Method: `POST`

### Request Body:
The request body should be a JSON object containing a `resume_url` key with the link to the PDF file you want to analyze, and a `job_description` key with the job description you want to use to build the resume.

**Example Request JSON:**

```json
{
  "resume_url": "https://utfs.io/f/uYCJGxAcJId8uk6is3AcJId8F3SNyhRlvDtHqWgfLOrVjk70",
  "job_description": "As an AI intern at Wastelink, you'll have the opportunity to work on cutting-edge solutions. Your role will involve using your knowledge of artificial intelligence and machine learning to develop innovative tools and algorithms that will contribute to our sustainability efforts."
}
```

**Example Response JSON:**

```json
{
  "generated_resume": "As an AI intern at Wastelink, you'll have the opportunity to work on cutting-edge solutions. Your role will involve using your knowledge of artificial intelligence and machine learning to develop innovative tools and algorithms that will contribute to our sustainability efforts.\n\nResponsibilities include building a prototype, data annotation, model training using frameworks like TensorFlow or PyTorch, and integration with warehouse management systems.\n\nThis is an excellent opportunity to gain hands-on experience in AI and machine learning, contributing to the automation and efficiency of our warehousing processes.\n\nIf you are a passionate and driven individual with a strong background in AI and machine learning, this internship at Wastelink is the perfect opportunity to gain hands-on experience and make a real impact in the field of sustainable waste management. Apply now and join us in shaping a cleaner and greener future!\n\nAbout Company: Wastelink is a food surplus management company that helps food manufacturers manage their surplus and waste by transforming it into nutritional feeds for animals."
}
```

## Recommendation
### Endpoint: `/recommendation`

### Method: `POST`

### Request Body:
The request body should be a JSON object containing a `resume_url` key with the link to the PDF file you want to analyze, and a `job_description` key with the job description you want to use to build the resume.

**Example Request JSON:**

```json
{
  "resume_url": "https://utfs.io/f/uYCJGxAcJId8uk6is3AcJId8F3SNyhRlvDtHqWgfLOrVjk70",
  "job_description": "As an AI intern at Wastelink, you'll have the opportunity to work on cutting-edge solutions. Your role will involve using your knowledge of artificial intelligence and machine learning to develop innovative tools and algorithms that will contribute to our sustainability efforts."
}
```

**Example Response JSON:**

```json
{
  "response": "As an AI intern at Wastelink, you'll have the opportunity to work on cutting-edge solutions. Your role will involve using your knowledge of artificial intelligence and machine learning to develop innovative tools and algorithms that will contribute to our sustainability efforts.\n\nResponsibilities include building a prototype, data annotation, model training using frameworks like TensorFlow or PyTorch, and integration with warehouse management systems.\n\nThis is an excellent opportunity to gain hands-on experience in AI and machine learning, contributing to the automation and efficiency of our warehousing processes.\n\nIf you are a passionate and driven individual with a strong background in AI and machine learning, this internship at Wastelink is the perfect opportunity to gain hands-on experience and make a real impact in the field of sustainable waste management. Apply now and join us in shaping a cleaner and greener future!\n\nAbout Company: Wastelink is a food surplus management company that helps food manufacturers manage their surplus and waste by transforming it into nutritional feeds for animals."
}
```