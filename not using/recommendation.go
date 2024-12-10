package main

import (
	"fmt"
	"os"

	"github.com/jpoz/groq"
)

func getBotResponse(apiKey, userInput, resumeText string) (string, error) {
	var client *groq.Client

	if apiKey == "" {
		apiKey = os.Getenv("GROQ_API_KEY")
	}
	client = groq.NewClient(groq.WithAPIKey(apiKey))
	messages := []groq.Message{
		{
			Role:    "system",
			Content: "You Are A Profile Analyser Analyse The Interviews Profile Professionally",
		},
		{
			Role:    "user",
			Content: fmt.Sprintf("Respond to this prompt %s using this data %s", userInput, resumeText),
		},
	}

	request := groq.CompletionCreateParams{
		Model:     "llama3-8b-8192",
		Messages:  messages,
		MaxTokens: 1000,
	}

	response, err := client.CreateChatCompletion(request)
	if err != nil {
		return "", err
	}

	return response.Choices[0].Message.Content, nil
}

func generateRecommendation(apiKey, resumeText, jobDescription string) (string, error) {
	query := fmt.Sprintf(`
Job Description:

You will critically and in a high level analyze a job seeker's profile based on the following job description and evaluate it across several key parameters. Provide an overall rating out of 100, considering the alignment of the job seeker’s profile which is given to you with the job description. The parameters you should consider are: Skills Match, Experience, Education, Accomplishments, Cultural Fit, Geographical Fit, Career Progression, Availability, Industry Knowledge, and Recommendations/References.

---

Job Description:

%s
---
Instructions:

1. Skills Match (0-20 points):
- Evaluate how well the job seeker's technical and soft skills align with the job requirements.

2. Experience (0-20 points):
- Consider the relevance of the job seeker's years of experience, prior roles, and industry experience to the job description.

3. Education (0-10 points):
- Assess the relevance of the job seeker’s educational background, including degrees and certifications, to the job requirements.

4. Accomplishments (0-10 points):
- Evaluate the significance of the job seeker's professional achievements and project experience in relation to the job description.

5. Cultural Fit (0-10 points):
- Determine how well the job seeker’s values and adaptability align with the company’s culture and work environment.

6. Geographical Fit (0-5 points):
- Consider the job seeker’s location in relation to the job location and their willingness to relocate, if necessary.

7. Career Progression (0-10 points):
- Evaluate the job seeker’s career growth trajectory and their ability to take on increasing responsibilities.

8. Availability (0-5 points):
- Assess the job seeker’s availability to start work and their willingness to commit to the company.

9. Industry Knowledge (0-5 points):
- Evaluate the job seeker’s understanding of industry trends and market conditions, and their ability to contribute valuable insights.

10. Recommendations/References (0-5 points):
- Assess the quality and relevance of the job seeker’s recommendations or references.

---
Output format:

Overall Rating: [Sum of all points out of 100]

Strengths:
- [Strength 1]
- [Strength 2]
- ...

Weaknesses:
- [Weakness 1]
- [Weakness 2]
- ...

Overall Assessment:
[Provide a brief summary of the job seeker’s strengths and weaknesses in relation to the job description, highlighting the key factors that influenced the overall rating.]
`, jobDescription)

	return getBotResponse(apiKey, query, resumeText)
}

// func main() {
// 	resumeText := "Your resume text here"
// 	jobDescription := "Job description here"

// 	recommendation, err := generateRecommendation(resumeText, jobDescription)
// 	if err != nil {
// 		fmt.Println("Error generating recommendation:", err)
// 		return
// 	}

// 	fmt.Println("Recommendation:")
// 	fmt.Println(recommendation)
// }
